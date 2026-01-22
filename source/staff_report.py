import logging
import os
import re

import xlsxwriter

from source.appdata import AppData
from source.competency_display import set_competency_status, create_report_worksheet, write_row, format_status_column
from source.write_cell import write_cell, yn

logger = logging.getLogger(__name__)


def staff_report(ad: AppData, report_excel_path: str, service_code_list, staff_type_list) -> None:
    """Generate a spreadsheet with a staff summary tab and tab for each staff member
       giving the status for each competency."""
    logger.info(f"Creating Staff Report for Service Areas {service_code_list} and Staff Types {staff_type_list}")

    # Define report work book and formats to be used
    wb = xlsxwriter.Workbook(report_excel_path)
    base_format = {'border': 1, 'valign': 'vcentre'}
    formats = {
        'plain': wb.add_format(base_format),
        'bold': wb.add_format(base_format | {'bold': True, 'align': 'centre'}),
        'header': wb.add_format(base_format | {'bg_color': '#2CC985', 'text_wrap': True}),
        'centre': wb.add_format(base_format | {'align': 'centre'}),
        'date': wb.add_format(base_format | {'num_format': 'dd.mm.yy', 'align': 'centre'}),
        'hyper': wb.add_format(base_format | {'font_color': 'blue', 'underline': 1})
    }

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
    header = [
        {'label': 'Staff Name', 'width': 26},
        {'label': 'Out Standing Competencies', 'width': 12},
        {'label': 'Service', 'width': 10},
        {'label': 'RN', 'width': 10},
        {'label': 'Role', 'width': 10},
        {'label': 'Nightshift', 'width': 10},
        {'label': 'Bank', 'width': 10}
    ]
    for status in range(len(ad.status_dict)):
        header.append({'label': ad.status_dict[status]['description'], 'width': 11})
    ws_sum = create_report_worksheet(wb, 'Staff', header, formats['header'], protect_options, ad.args.report_password)
    ws_sum_row = 0

    # Process each staff member
    sheet_name_list = []
    for db_s in range(ad.md.len('Staff')):
        # Check staff member has a role in the selected Service Area and Staff Type
        staff_name = ad.md.get('Staff', 'Staff Name', db_s)
        staff_required = False
        for service_code in service_code_list:
            for staff_type in staff_type_list:
                db_sr = ad.md.find_two('Staff Role', staff_name, 'Staff Name', service_code, 'Service Code')
                if db_sr != -1:
                    role_code = ad.md.get('Staff Role', 'Role Code', db_sr)
                    db_r = ad.md.find_one('Role', role_code, 'Role Code')
                    rn = ad.md.get('Role', 'RN', db_r)
                    if staff_type == 'RN' and rn or staff_type == 'HCA' and not rn:
                        staff_required = True
                        break

        if not staff_required:
            continue

        # Set sheet name and check it does not already exist, sheet duplicates are case-insensitive
        sheet_name = re.sub(r'[^a-zA-Z]', ' ', staff_name)[:30]
        duplicate_count = sheet_name_list.count(sheet_name.lower())
        sheet_name_list.append(sheet_name.lower())
        if duplicate_count > 0:
            length_number = int(duplicate_count / 10) + 2
            sheet_name = sheet_name[:30-length_number] + ' ' + str(duplicate_count)

        # Create staff sheet and output header row
        header = [
            {'label': 'Status', 'width': 20},
            {'label': 'Competency Name', 'width': 32},
            {'label': 'Scope', 'width': 10},
            {'label': 'Expiry', 'width': 10},
            {'label': 'Prerequisite', 'width': 12},
            {'label': 'Nightshift', 'width': 10},
            {'label': 'Bank', 'width': 10},
            {'label': 'Competency Date', 'width': 12},
            {'label': 'Completed', 'width': 10},
            {'label': 'Prerequisite Date', 'width': 12},
            {'label': 'Achieved', 'width': 10},
            {'label': 'Notes', 'width': 35},
            {'label': 'Force Not Required', 'width': 10},
            {'label': 'Force Required', 'width': 10},
            {'label': 'Staff', 'width': 12}
        ]
        ws_stf = create_report_worksheet(wb, sheet_name, header,
                                         formats['header'], protect_options, ad.args.report_password)
        ws_stf.write_url(0, len(header) - 1, f"internal:'Staff'!A{db_s + 2}", formats['hyper'], string='Staff')
        ws_stf_row = 0

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
                    ws_stf_row += 1
                    db_sc = ad.md.find_two('Staff Competency', staff_name, 'Staff Name',
                                           ad.md.get('Competency', 'Competency Name', db_c), 'Competency Name')
                    data = [
                        {'value': ad.status_dict[status]['description']},
                        {'value': ad.md.get('Competency', 'Competency Name', db_c)},
                        {'value': ad.md.get('Competency', 'Scope', db_c)},
                        {'value': ad.md.get('Competency', 'Expiry', db_c)},
                        {'value': yn(ad.md.get('Competency', 'Prerequisite', db_c)),
                         'format': 'centre'},
                        {'value': yn(ad.md.get('Competency', 'Nightshift', db_c)),
                         'format': 'centre'},
                        {'value': yn(ad.md.get('Competency', 'Bank', db_c)),
                         'format': 'centre'},
                        {'value': ad.md.get('Staff Competency', 'Competency Date', db_sc) if db_sc > -1 else '',
                         'format': 'date'},
                        {'value': yn(ad.md.get('Staff Competency', 'Completed', db_sc)) if db_sc > -1 else ''},
                        {'value': ad.md.get('Staff Competency', 'Prerequisite Date', db_sc) if db_sc > -1 else '',
                         'format': 'date'},
                        {'value': yn(ad.md.get('Staff Competency', 'Achieved', db_sc)) if db_sc > -1 else ''},
                        {'value': ad.md.get('Staff Competency', 'Notes', db_sc) if db_sc > -1 else ''},
                        {'value': yn(ad.md.get('Staff Competency', 'Not Required', db_sc)) if db_sc > -1 else ''},
                        {'value': yn(ad.md.get('Staff Competency', 'Required', db_sc)) if db_sc > -1 else ''}
                    ]
                    write_row(ws_stf, ws_stf_row, data, formats)
                    row_status.append(status)

        format_status_column(ws_stf, row_status, ad, wb)

        # Add filter to first 7 columns of staff sheet
        ws_stf.autofilter(0, 0, ws_stf_row, 6)
        ws_stf.set_header('&L&14&A - &D')

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
                         formats['hyper'], string=staff_name)
        ws_sum_col = 1
        outstanding = status_count[0] + status_count[1] + status_count[2]
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, outstanding, formats['bold'])
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, service_code_txt[:-2], formats['plain'])
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, rn_txt[:-2], formats['centre'])
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, role_code_txt[:-2], formats['plain'])
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, nightshift_txt[:-2], formats['centre'])
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, bank_txt[:-2], formats['centre'])
        for status in range(len(ad.status_dict)):
            ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, status_count[status], formats['plain'])

    # Add filter to first 7 columns of summary sheet
    ws_sum.autofilter(0, 0, ws_sum_row, 6)
    ws_sum.set_header('&L&14&A - &D')

    # Save spreadsheet and open it
    wb.close()
    os.startfile(report_excel_path)
