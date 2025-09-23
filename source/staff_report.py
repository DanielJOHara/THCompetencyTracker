"""This module contains the routine to generate the Staff report. This report is a spreadsheet with
   a staff summary tab and tab for each staff member giving the status for each competency."""
import logging
import os
import re

import xlsxwriter

from source.appdata import AppData
from source.competency_display import set_competency_status
from source.write_cell import write_cell, yn

logger = logging.getLogger(__name__)


def staff_report(ad: AppData, report_excel_path: str) -> None:
    """Generate a spreadsheet with a staff summary tab and tab for each staff member
       giving the status for each competency."""
    logger.info("Creating Staff Report")

    # Define report work book and formats to be used
    wb = xlsxwriter.Workbook(report_excel_path)
    base_format = {'border': 1, 'valign': 'vcentre'}
    format_plain = wb.add_format(base_format)
    format_bold = wb.add_format(base_format | {'bold': True, 'align': 'centre'})
    format_header = wb.add_format(base_format | {'bg_color': '#2CC985', 'text_wrap': True})
    format_centre = wb.add_format(base_format | {'align': 'centre'})
    format_date = wb.add_format(base_format | {'num_format': 'dd.mm.yy', 'align': 'centre'})
    format_hyper = wb.add_format(base_format | {'font_color': 'blue', 'underline': 1})

    # Define the sheet protect option
    protect_options = {
        'objects': False,
        'scenarios': False,
        'format_cells': True,
        'format_columns': True,
        'format_rows': True,
        'insert_columns': False,
        'insert_rows': False,
        'insert_hyperlinks': False,
        'delete_columns': False,
        'delete_rows': False,
        'select_locked_cells': True,
        'sort': False,
        'autofilter': True,
        'pivot_tables': False,
        'select_unlocked_cells': True,
    }

    # Create Staff summary sheet and output header row
    ws_sum = wb.add_worksheet('Staff')
    ws_sum.hide_gridlines(2)
    ws_sum.freeze_panes(1, 0)
    ws_sum_row = 0
    ws_sum_col = 0
    ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, 'Staff Name', format_header, width=26)
    ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, 'Out Standing Competencies', format_header, width=12)
    ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, 'Service', format_header, width=10)
    ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, 'RN', format_header, width=10)
    ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, 'Role', format_header, width=10)
    ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, 'Nightshift', format_header, width=10)
    ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, 'Bank', format_header, width=10)
    for status in range(len(ad.status_dict)):
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, ad.status_dict[status]['description'],
                                format_header, width=11)

    # Process each staff member
    sheet_name_list = []
    for db_s in range(ad.md.len('Staff')):
        # Set sheet name and check it does not already exist, sheet duplicates are case-insensitive
        staff_name = ad.md.get('Staff', 'Staff Name', db_s)
        sheet_name = re.sub(r'[\[\]:*?/\\]', ' ', ad.md.get('Staff', 'Staff Name', db_s))[:30]
        duplicate_count = sheet_name_list.count(sheet_name.lower())
        sheet_name_list.append(sheet_name.lower())
        if duplicate_count > 0:
            length_number = int(duplicate_count / 10) + 2
            sheet_name = sheet_name[:30-length_number] + ' ' + str(duplicate_count)

        # Create staff sheet and output header row
        ws_stf = wb.add_worksheet(sheet_name)
        ws_stf.hide_gridlines(2)
        ws_stf.freeze_panes(1, 0)
        ws_stf_row = 0
        ws_stf_col = 0
        ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, 'Status', format_header, width=20)
        ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, 'Competency Name', format_header, width=32)
        ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, 'Scope', format_header, width=10)
        ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, 'Expiry', format_header, width=10)
        ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, 'Prerequisite', format_header, width=12)
        ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, 'Nightshift', format_header, width=10)
        ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, 'Bank', format_header, width=10)
        ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, 'Competency Date', format_header, width=12)
        ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, 'Completed', format_header, width=10)
        ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, 'Prerequisite Date', format_header, width=12)
        ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, 'Achieved', format_header, width=10)
        ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, 'Notes', format_header, width=35)
        ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, 'Force Not Required', format_header, width=10)
        ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, 'Force Required', format_header, width=10)
        ws_stf.write_url(ws_stf_row, ws_stf_col, f"internal:'Staff'!A{db_s + 2}", format_hyper, string='Staff')

        # Create list of competency statuses for staff member
        competency_status_list = []
        for db_c in range(ad.md.len('Competency')):
            status = set_competency_status(ad, db_s, db_c, ad.md.get_list('Service', 'Service Code'))
            competency_status_list.append(status)

        # Write a row (excluding first colum) for each staff member in status blocks
        status_count = [0] * len(ad.status_dict)  # Initialise status count for summary row
        row_status = [None]  # List to store status for each staff member, the first entry is None and will not be used
        for status in range(len(ad.status_dict)):
            for db_c in range(ad.md.len('Competency')):
                if competency_status_list[db_c] == status:
                    status_count[status] += 1
                    competency_name = ad.md.get('Competency', 'Competency Name', db_c)
                    db_sc = ad.md.find_two('Staff Competency',
                                           staff_name, 'Staff Name',
                                           competency_name, 'Competency Name')

                    if db_sc > -1:
                        competency_date = ad.md.get('Staff Competency', 'Competency Date', db_sc)
                        completed = yn(ad.md.get('Staff Competency', 'Completed', db_sc))
                        prerequisite_date = ad.md.get('Staff Competency', 'Prerequisite Date', db_sc)
                        achieved = yn(ad.md.get('Staff Competency', 'Achieved', db_sc))
                        notes = ad.md.get('Staff Competency', 'Notes', db_sc)
                        not_required = yn(ad.md.get('Staff Competency', 'Not Required', db_sc))
                        required = yn(ad.md.get('Staff Competency', 'Required', db_sc))
                    else:
                        competency_date = ''
                        completed = ''
                        prerequisite_date = ''
                        achieved = ''
                        notes = ''
                        not_required = ''
                        required = ''
                    ws_stf_row += 1
                    ws_stf_col = 1
                    ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col,
                                            ad.md.get('Competency', 'Competency Name', db_c), format_plain)
                    ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col,
                                            ad.md.get('Competency', 'Scope', db_c), format_plain)
                    ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col,
                                            ad.md.get('Competency', 'Expiry', db_c), format_plain)
                    ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col,
                                            yn(ad.md.get('Competency', 'Prerequisite', db_c)), format_centre)
                    ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col,
                                            yn(ad.md.get('Competency', 'Nightshift', db_c)), format_centre)
                    ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col,
                                            yn(ad.md.get('Competency', 'Bank', db_c)), format_centre)
                    ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, competency_date, format_date)
                    ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, completed, format_centre)
                    ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, prerequisite_date, format_date)
                    ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, achieved, format_centre)
                    ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, notes, format_plain)
                    ws_stf_col = write_cell(ws_stf, ws_stf_row, ws_stf_col, not_required, format_centre)
                    write_cell(ws_stf, ws_stf_row, ws_stf_col, required, format_centre)
                    row_status.append(status)

        # Write first column with status description with background colour and
        # a border around rows with the same status
        for row in range(1, len(row_status)):
            status_colour = ad.status_dict[row_status[row]]['colour']

            status_format = {'valign': 'vcentre', 'bg_color': status_colour}

            # Test if this is the only row with this status
            if row_status[row] != row_status[row - 1] and (
                    row == len(row_status) - 1 or row_status[row] != row_status[row + 1]):
                this_format = wb.add_format(status_format | {'border': 1})

            # Test if this is the first row with this status
            elif row_status[row] != row_status[row - 1]:
                this_format = wb.add_format(status_format | {'top': 1, 'left': 1, 'right': 1})

            # Test if this is the last row with this status
            elif row == len(row_status) - 1 or row_status[row] != row_status[row + 1]:
                this_format = wb.add_format(
                    status_format | {'bottom': 1, 'left': 1, 'right': 1, 'font_color': status_colour})

            # This is a middle row for this status
            else:
                this_format = wb.add_format(status_format | {'left': 1, 'right': 1, 'font_color': status_colour})

            write_cell(ws_stf, row, 0, ad.status_dict[row_status[row]]['description'], this_format)

        # Add filter to first 7 columns of staff sheet
        ws_stf.autofilter(0, 0, ws_stf_row, 6)
        ws_stf.set_header('&L&14&A - &D')
        ws_stf.protect(ad.args.report_password, protect_options)

        # Concatenate role information for this staff member's summary row
        service_code_txt = ''
        rn_txt = ''
        role_code_txt = ''
        nightshift_txt = ''
        bank_txt = ''
        for service_code in ad.md.get_list('Service', 'Service Code'):
            db_sr = ad.md.find_two('Staff Role',
                                   service_code, 'Service Code',
                                   staff_name, 'Staff Name')
            if db_sr > -1:
                service_code_txt += ad.md.get('Staff Role', 'Service Code', db_sr) + ', '
                db_r = ad.md.find_one('Role', ad.md.get('Staff Role', 'Role Code', db_sr), 'Role Code')
                rn_txt += yn(ad.md.get('Role', 'RN', db_r)) + ', '
                role_code_txt += ad.md.get('Staff Role', 'Role Code', db_sr) + ', '
                nightshift_txt += yn(ad.md.get('Staff Role', 'Nightshift', db_sr)) + ', '
                bank_txt += yn(ad.md.get('Staff Role', 'Bank', db_sr)) + ', '

        # Write row for staff member to summary sheet
        ws_sum_row += 1
        ws_sum.write_url(ws_sum_row, 0, f"internal:'{sheet_name}'!A1",
                         format_hyper, string=ad.md.get('Staff', 'Staff Name', db_s))
        ws_sum_col = 1
        outstanding = status_count[0] + status_count[1] + status_count[2]
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, outstanding, format_bold)
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, service_code_txt[:-2], format_plain)
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, rn_txt[:-2], format_centre)
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, role_code_txt[:-2], format_plain)
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, nightshift_txt[:-2], format_centre)
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, bank_txt[:-2], format_centre)
        for status in range(len(ad.status_dict)):
            ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, status_count[status], format_plain)

    # Add filter to first 7 columns of summary sheet
    ws_sum.autofilter(0, 0, ws_sum_row, 6)
    ws_sum.set_header('&L&14&A - &D')
    ws_sum.protect(ad.args.report_password, protect_options)

    # Save spreadsheet and open it
    wb.close()
    os.startfile(report_excel_path)
