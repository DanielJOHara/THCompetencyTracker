"""This module exports the competency grids to sheets on a spreadsheet.
   There is a tab for each Service Code and Staff Type (RN and HCA) combination."""
import logging
import os

import xlsxwriter

from source.appdata import AppData
from source.competency_display import set_display_value, staff_competency_lists
from source.write_cell import write_cell, write_cell_y

logger = logging.getLogger(__name__)


def competency_grid_export(ad: AppData, report_excel_path: str, service_code_list, staff_type_list) -> None:
    """Export the competency grids for specified service codes and staff types to sheets on a spreadsheet."""
    logger.info("Exporting Competency Grid")

    # Define report work book and formats to be used
    wb = xlsxwriter.Workbook(report_excel_path)
    base_format = {'border': 1, 'valign': 'vcentre'}
    format_wrap = wb.add_format(base_format | {'text_wrap': True})
    format_wrap_grey = wb.add_format(base_format | {'text_wrap': True, 'bg_color': '#D3D3D3'})
    format_plain = wb.add_format(base_format)
    format_centre = wb.add_format(base_format | {'align': 'centre'})
    format_centre_red = wb.add_format(base_format | {'align': 'centre', 'color': 'red', 'bold': True})
    format_date = wb.add_format(base_format | {'num_format': 'dd.mm.yy', 'align': 'centre'})

    competence_format = base_format | {'text_wrap': True, 'num_format': 'dd.mm.yy', 'align': 'centre'}

    # Formats used for key
    format_out_of_date = wb.add_format(competence_format | {'bg_color': ad.status_dict[0]['colour']})
    format_ft_needed = wb.add_format(competence_format | {'bg_color': ad.status_dict[1]['colour']})
    format_needed = wb.add_format(competence_format | {'bg_color': ad.status_dict[2]['colour']})
    format_next_3_months = wb.add_format(competence_format | {'bg_color': ad.status_dict[3]['colour']})
    format_in_date = wb.add_format(competence_format | {'bg_color': ad.status_dict[4]['colour']})
    format_not_required = wb.add_format(competence_format | {'bg_color': ad.status_dict[5]['colour']})

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

    # Loop for each sheet, there will be an RN and HCA sheet for each service that has staff
    for service_code in service_code_list:
        for staff_type in staff_type_list:
            # Create a database object of Staff and Competency tables for the
            # Service Code and Staff Type combination
            db_s_list, db_c_list = staff_competency_lists(ad, service_code, staff_type)

            # Define work sheet for the RN or HCA for the service
            ws = wb.add_worksheet(f'{service_code} {staff_type}s')
            ws.hide_gridlines(2)
            ws.freeze_panes(2, 1)
            ws.set_zoom(75)
            ws.set_default_row(44)

            # Write first header row
            rn_flg = staff_type == 'RN'
            col = write_cell(ws, 0, 0, 'Staff Name', format_wrap, width=26)
            col = write_cell(ws, 0, col, 'Start Date', format_wrap, width=10)
            col = write_cell(ws, 0, col, 'Job Role', format_wrap, width=10)
            if rn_flg:
                col = write_cell(ws, 0, col, 'Practice Supervisor', format_wrap, width=10)
                col = write_cell(ws, 0, col, 'Practice Assessor', format_wrap, width=10)
            for db_c in db_c_list:
                col = write_cell(ws, 0, col,
                                 ad.md.get('Competency', 'Competency Name', db_c), format_wrap_grey, width=15)

            # Write second header row
            col = write_cell(ws, 1, 0, service_code + ' - ' + staff_type, format_wrap_grey)
            col = write_cell(ws, 1, col, '', format_wrap_grey)
            col = write_cell(ws, 1, col, '', format_wrap_grey)
            if rn_flg:
                col = write_cell(ws, 1, col, '', format_wrap_grey)
                col = write_cell(ws, 1, col, '', format_wrap_grey)
            for db_c in db_c_list:
                competency_expiry = ad.md.get('Competency', 'Expiry', db_c)
                if competency_expiry:
                    col = write_cell(ws, 1, col, str(competency_expiry) + ' Yearly', format_centre_red)
                else:
                    col = write_cell(ws, 1, col, 'Once Only', format_centre)

            row = 1
            last_role_code = None
            last_staff_bank = 0
            for db_s in db_s_list:
                row += 1
                staff_name = ad.md.get('Staff', 'Staff Name', db_s)
                db_sr = ad.md.find_two('Staff Role',
                                       service_code, 'Service Code',
                                       staff_name, 'Staff Name')
                if db_sr < 0:
                    continue
                role_code = ad.md.get('Staff Role', 'Role Code', db_sr)
                staff_nightshift = ad.md.get('Staff Role', 'Nightshift', db_sr)
                staff_bank = ad.md.get('Staff Role', 'Bank', db_sr)

                # Output Bank row at start of bank staff or blank row for staff role changes
                if staff_bank and not last_staff_bank:
                    write_cell(ws, row, 0, "Bank", format_wrap_grey)
                    row += 1
                elif last_role_code and role_code != last_role_code:
                    ws.set_row(row, 15)
                    row += 1
                last_role_code = role_code
                last_staff_bank = staff_bank

                if staff_nightshift:
                    staff_name_nightshift = staff_name + ' (nights)'
                else:
                    staff_name_nightshift = staff_name
                col = write_cell(ws, row, 0, staff_name_nightshift, format_plain)
                col = write_cell(ws, row, col, ad.md.get('Staff', 'Start Date', db_s), format_date)
                col = write_cell(ws, row, col, role_code, format_centre)
                if rn_flg:
                    col = write_cell_y(ws, row, col, ad.md.get('Staff', 'Practice Supervisor', db_s), format_centre)
                    col = write_cell_y(ws, row, col, ad.md.get('Staff', 'Practice Assessor', db_s), format_centre)

                for db_c in db_c_list:
                    display_value, colour = set_display_value(ad, service_code, db_s, db_c)
                    display_format = wb.add_format(competence_format | {'bg_color': colour})

                    col = write_cell(ws, row, col, display_value, display_format)

            write_cell(ws, row + 2, 0, 'Key', format_centre)
            write_cell(ws, row + 3, 0, 'Not Required For Role', format_not_required)
            write_cell(ws, row + 4, 0, 'Out of Date', format_out_of_date)
            write_cell(ws, row + 5, 0, 'Within 3 Months', format_next_3_months)
            write_cell(ws, row + 6, 0, 'In Date', format_in_date)
            write_cell(ws, row + 7, 0, 'FT Needed', format_ft_needed)
            write_cell(ws, row + 8, 0, 'Competency Needed', format_needed)

            # Add filters to staff name and roles
            if staff_type == 'RN':
                ws.autofilter(1, 0, row - 1, 4)
            else:
                ws.autofilter(1, 0, row - 1, 2)
            ws.set_header('&L&14&A - &D')
            ws.protect(ad.args.report_password, protect_options)

    wb.close()
    os.startfile(report_excel_path)
