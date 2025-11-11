import logging
import os
import re

import xlsxwriter

from source.appdata import AppData
from source.competency_display import set_competency_status, create_report_worksheet, write_row, format_status_column
from source.write_cell import write_cell, yn

logger = logging.getLogger(__name__)


def competency_report(ad: AppData, service_code: str, staff_type: str, report_excel_path: str) -> None:
    """Generate a spreadsheet with a tab for each competency giving the status for each staff member."""
    logger.info(f"Creating Competency Report for Service Code {service_code} and Staff Type {staff_type}")

    # Define report work book and formats to be used
    wb = xlsxwriter.Workbook(report_excel_path)
    base_format = {'border': 1, 'valign': 'vcentre'}
    formats = {
        'plain': wb.add_format(base_format),
        'light_grey': wb.add_format(base_format | {'bg_color': '#D9D9D9'}),
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

    # Create Competency summary sheet and output header row
    header = [
        {'label': 'Competency Name', 'width': 32},
        {'label': 'Scope', 'width': 10},
        {'label': 'Expiry', 'width': 10},
        {'label': 'Prerequisite', 'width': 12},
        {'label': 'Nightshift', 'width': 10},
        {'label': 'Bank', 'width': 10}
    ]
    for status in range(len(ad.status_dict)):
        header.append({'label': ad.status_dict[status]['description'], 'width': 11})
    ws_sum = create_report_worksheet(wb, 'Competency', header, formats['header'], protect_options, ad.args.report_password)
    ws_sum_row = 0

    # Process each competency
    for db_c in range(ad.md.len('Competency')):
        competency_name = ad.md.get('Competency', 'Competency Name', db_c)
        # Create competency sheet and output header row
        sheet_name = re.sub(r'[[\]:*?/\\]', ' ', competency_name)[:30]
        header = [
            {'label': 'Status', 'width': 20},
            {'label': 'Staff Name', 'width': 26},
            {'label': 'Service', 'width': 10},
            {'label': 'RN', 'width': 10},
            {'label': 'Role', 'width': 10},
            {'label': 'Nightshift', 'width': 10},
            {'label': 'Bank', 'width': 10},
            {'label': 'Competency Date', 'width': 12},
            {'label': 'Completed', 'width': 10},
            {'label': 'Prerequisite Date', 'width': 12},
            {'label': 'Achieved', 'width': 10},
            {'label': 'Notes', 'width': 35},
            {'label': 'Force Not Required', 'width': 10},
            {'label': 'Force Required', 'width': 10},
            {'label': 'Competency', 'width': 12}
        ]
        ws_cmp = create_report_worksheet(wb, sheet_name, header, formats['header'], protect_options, ad.args.report_password)
        ws_cmp.write_url(0, len(header) - 1, f"internal:'Competency'!A{db_c + 2}", formats['hyper'], string='Competency')
        ws_cmp_row = 0

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

            # Add staff member's competency status and indexes to list
            status = set_competency_status(ad, db_s, db_c, [service_code])
            competency_status_list.append([status, db_s, db_sr])

        # Write a row (excluding first colum) for each competency in status blocks
        status_count = [0] * len(ad.status_dict)  # Initialise counts for each status
        row_status = [None]  # List to store status for each competency, the first entry is None and will not be used
        for status in range(len(ad.status_dict)):
            for competency_status in competency_status_list:
                if competency_status[0] == status:
                    status_count[status] += 1
                    ws_cmp_row += 1
                    db_s = competency_status[1]
                    db_sr = competency_status[2]
                    db_sc = ad.md.find_two('Staff Competency', ad.md.get('Staff', 'Staff Name', db_s), 'Staff Name', competency_name, 'Competency Name')
                    data = [
                        {'value': ad.status_dict[status]['description']},
                        {'value': ad.md.get('Staff', 'Staff Name', db_s)},
                        {'value': ad.md.get('Staff Role', 'Service Code', db_sr)},
                        {'value': yn(ad.md.get('Role', 'RN', ad.md.find_one('Role', ad.md.get('Staff Role', 'Role Code', db_sr), 'Role Code'))), 'format': 'centre'},
                        {'value': ad.md.get('Staff Role', 'Role Code', db_sr)},
                        {'value': yn(ad.md.get('Staff Role', 'Nightshift', db_sr)), 'format': 'centre'},
                        {'value': yn(ad.md.get('Staff Role', 'Bank', db_sr)), 'format': 'centre'},
                        {'value': ad.md.get('Staff Competency', 'Competency Date', db_sc) if db_sc > -1 else ''},
                        {'value': yn(ad.md.get('Staff Competency', 'Completed', db_sc)) if db_sc > -1 else ''},
                        {'value': ad.md.get('Staff Competency', 'Prerequisite Date', db_sc) if db_sc > -1 else ''},
                        {'value': yn(ad.md.get('Staff Competency', 'Achieved', db_sc)) if db_sc > -1 else ''},
                        {'value': ad.md.get('Staff Competency', 'Notes', db_sc) if db_sc > -1 else ''},
                        {'value': yn(ad.md.get('Staff Competency', 'Not Required', db_sc)) if db_sc > -1 else ''},
                        {'value': yn(ad.md.get('Staff Competency', 'Required', db_sc)) if db_sc > -1 else ''}
                    ]
                    write_row(ws_cmp, ws_cmp_row, data, formats)
                    row_status.append(status)

        format_status_column(ws_cmp, row_status, ad, wb)

        # Add filter to first 7 columns of competency sheet
        ws_cmp.autofilter(0, 0, ws_cmp_row, 6)
        ws_cmp.set_header('&L&14&A - &D')

        # Write row for competency to summary sheet
        ws_sum_row += 1
        ws_sum.write_url(ws_sum_row, 0, f"internal:'{sheet_name}'!A1", formats['hyper'],
                         string=competency_name)
        ws_sum_col = 1
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, ad.md.get('Competency', 'Scope', db_c), formats['plain'])
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, ad.md.get('Competency', 'Expiry', db_c), formats['plain'])
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col,
                                yn(ad.md.get('Competency', 'Prerequisite', db_c)), formats['centre'])
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col,
                                yn(ad.md.get('Competency', 'Nightshift', db_c)), formats['centre'])
        ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col,
                                yn(ad.md.get('Competency', 'Bank', db_c)), formats['centre'])
        for status in range(len(ad.status_dict)):
            if (
                    status == 0 and not ad.md.get('Competency', 'Expiry', db_c)
                    or status == 1 and not ad.md.get('Competency', 'Prerequisite', db_c)
                ):
                ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, '', formats['light_grey'])
            else:
                ws_sum_col = write_cell(ws_sum, ws_sum_row, ws_sum_col, status_count[status], formats['plain'])

    # Add filter to first 6 columns of summary sheet
    ws_sum.autofilter(0, 0, ws_sum_row, 5)
    ws_sum.set_header('&L&14&A - &D')

    wb.close()
    os.startfile(report_excel_path)
