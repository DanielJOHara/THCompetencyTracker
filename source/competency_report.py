"""This module contains the routine to generate the Competency report. This report is a spreadsheet with
   a competency summary tab and tab for each competency giving the status for each staff member."""
import logging
import os
import re

import xlsxwriter

from source.appdata import AppData
from source.competency_display import set_competency_status
from source.write_cell import write_cell, yn

logger = logging.getLogger(__name__)


def competency_report(ad: AppData, service_code: str, staff_type: str, report_excel_path: str) -> None:
    """Generate a spreadsheet with a tab for each competency giving the status for each staff member."""
    logger.info(f"Creating Competency Report for Service Code {service_code} and Staff Type {staff_type}")

    # Define report work book and formats to be used
    wb = xlsxwriter.Workbook(report_excel_path)
    base_format = {'border': 1, 'valign': 'vcentre'}
    format_plain = wb.add_format(base_format)
    format_light_grey = wb.add_format(base_format | {'bg_color': '#D9D9D9'})
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

    # Create Competency summary sheet and output header row
    ws_sum = wb.add_worksheet('Competency')
    ws_sum.hide_gridlines(2)
    ws_sum.freeze_panes(1, 0)
    ws_sum_row = 0
    ws_sum_col = 0
    ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, 'Competency Name', format_header, width=32)
    ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, 'Scope', format_header, width=10)
    ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, 'Expiry', format_header, width=10)
    ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, 'Prerequisite', format_header, width=12)
    ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, 'Nightshift', format_header, width=10)
    ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, 'Bank', format_header, width=10)
    for status in range(len(ad.status_dict)):
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, ad.status_dict[status]['description'],
                                format_header, width=11)

    # Process each competency
    for db_c in range(ad.md.len('Competency')):
        competency_name = ad.md.get('Competency', 'Competency Name', db_c)
        # Create competency sheet and output header row
        sheet_name = re.sub(r'[\[\]:*?/\\]', ' ', ad.md.get('Competency', 'Competency Name', db_c))[:30]
        ws_cmp = wb.add_worksheet(sheet_name)
        ws_cmp.hide_gridlines(2)
        ws_cmp.freeze_panes(1, 0)
        ws_cmp_row = 0
        ws_cmp_col = 0
        ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, 'Status', format_header, width=20)
        ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, 'Staff Name', format_header, width=26)
        ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, 'Service', format_header, width=10)
        ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, 'RN', format_header, width=10)
        ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, 'Role', format_header, width=10)
        ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, 'Nightshift', format_header, width=10)
        ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, 'Bank', format_header, width=10)
        ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, 'Competency Date', format_header, width=12)
        ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, 'Completed', format_header, width=10)
        ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, 'Prerequisite Date', format_header, width=12)
        ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, 'Achieved', format_header, width=10)
        ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, 'Notes', format_header, width=35)
        ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, 'Force Not Required', format_header, width=10)
        ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, 'Force Required', format_header, width=10)
        ws_cmp.write_url(ws_cmp_row, ws_cmp_col, f"internal:'Competency'!A{db_c + 2}", format_hyper,
                         string='Competency')

        # Create list of competency status for staff members with role in service
        # If they have no role for the service they will not be added to the status list
        competency_status_list = []
        for db_s in range(ad.md.len('Staff')):
            staff_name = ad.md.get('Staff', 'Staff Name', db_s)
            # Find staff members role for service and they don't have role skip them
            db_sr = ad.md.find_two('Staff Role',
                                   service_code,  'Service Code',
                                   staff_name, 'Staff Name')
            if db_sr < 0:
                continue

            # Look up the role and if it is not for a required staff type skip the staff member
            db_r = ad.md.index('Role', 'Role Code', ad.md.get('Staff Role', 'Role Code', db_sr))
            if (ad.md.get('Role', 'RN', db_r) and staff_type not in ['RN', 'BOTH']
                    or not ad.md.get('Role', 'RN', db_r) and staff_type not in ['HCA', 'BOTH']):
                continue

            # Find staff competency record if it exists
            db_sc = ad.md.find_two('Staff Competency',
                                   staff_name, 'Staff Name',
                                   competency_name, 'Competency Name')

            # Add staff member's competency status and indexes to list
            status = set_competency_status(ad, db_s, db_c, [service_code])
            competency_status_list.append([status, db_s, db_sr, db_sc])

        # Write a row (excluding first colum) for each competency in status blocks
        status_count = [0] * len(ad.status_dict)  # Initialise counts for each status
        row_status = [None]  # List to store status for each competency, the first entry is None and will not be used
        for status in range(len(ad.status_dict)):
            for competency_status in competency_status_list:
                db_s = competency_status[1]
                staff_name = ad.md.get('Staff', 'Staff Name', db_s)
                if competency_status[0] == status:
                    status_count[status] += 1
                    db_sr = competency_status[2]
                    db_r = ad.md.find_one('Role', ad.md.get('Staff Role', 'Role Code', db_sr), 'Role Code')
                    service_code = ad.md.get('Staff Role', 'Service Code', db_sr)
                    rn = yn(ad.md.get('Role', 'RN', db_r))
                    role_code = ad.md.get('Staff Role', 'Role Code', db_sr)
                    nightshift = yn(ad.md.get('Staff Role', 'Nightshift', db_sr))
                    bank = yn(ad.md.get('Staff Role', 'Bank', db_sr))
                    db_sc = competency_status[3]
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
                    ws_cmp_row += 1
                    ws_cmp_col = 1
                    ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, staff_name, format_plain)
                    ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, service_code, format_plain)
                    ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, rn, format_centre)
                    ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, role_code, format_plain)
                    ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, nightshift, format_centre)
                    ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, bank, format_centre)
                    ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, competency_date, format_date)
                    ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, completed, format_centre)
                    ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, prerequisite_date, format_date)
                    ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, achieved, format_centre)
                    ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, notes, format_plain)
                    ws_cmp_col = write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, not_required, format_centre)
                    write_cell(ws_cmp, ws_cmp_row, ws_cmp_col, required, format_centre)
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
                this_format = wb.add_format(status_format |
                                            {'bottom': 1, 'left': 1, 'right': 1, 'font_color': status_colour})

            # This is a middle row for this status
            else:
                this_format = wb.add_format(status_format | {'left': 1, 'right': 1, 'font_color': status_colour})

            write_cell(ws_cmp, row, 0, ad.status_dict[row_status[row]]['description'], this_format)

        # Add filter to first 7 columns of competency sheet
        ws_cmp.autofilter(0, 0, ws_cmp_row, 6)
        ws_cmp.set_header('&L&14&A - &D')
        ws_cmp.protect(ad.args.report_password, protect_options)

        # Write row for competency to summary sheet
        ws_sum_row += 1
        ws_sum.write_url(ws_sum_row, 0, f"internal:'{sheet_name}'!A1", format_hyper,
                         string=ad.md.get('Competency', 'Competency Name', db_c))
        ws_sum_col = write_cell(ws_sum, ws_sum_row, 1, ad.md.get('Competency', 'Scope', db_c), format_plain)
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, ad.md.get('Competency', 'Expiry', db_c), format_plain)
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col,
                                yn(ad.md.get('Competency', 'Prerequisite', db_c)), format_centre)
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col,
                                yn(ad.md.get('Competency', 'Nightshift', db_c)), format_centre)
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col,
                                yn(ad.md.get('Competency', 'Bank', db_c)), format_centre)
        for status in range(len(ad.status_dict)):
            if (status == 0 and not ad.md.get('Competency', 'Expiry', db_c)
                    or status == 1 and not ad.md.get('Competency', 'Prerequisite', db_c)):
                ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, '', format_light_grey)
            else:
                ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, status_count[status], format_plain)

    # Add filter to first 6 columns of summary sheet
    ws_sum.autofilter(0, 0, ws_sum_row, 5)
    ws_sum.set_header('&L&14&A - &D')
    ws_sum.protect(ad.args.report_password, protect_options)

    wb.close()
    os.startfile(report_excel_path)
