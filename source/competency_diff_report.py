import logging
import os

import xlsxwriter

from appdata import AppData
from competency_differences import CompetencyDifferences
from excel_functions import create_report_worksheet, write_cell

logger = logging.getLogger(__name__)


def competency_diff_report(report_path: str, diff: CompetencyDifferences) -> None:
    """Generate a spreadsheet with a tab for each competency giving the status for each staff member."""
    logger.info(f"Creating Competency Differance Report {report_path}")

    # Define report work book and formats to be used
    wb = xlsxwriter.Workbook(report_path)
    base_format = {'border': 1, 'valign': 'vcentre'}
    formats = {
        'plain': wb.add_format(base_format),
        'header': wb.add_format(base_format | {'bg_color': '#2CC985', 'text_wrap': True}),
        'date': wb.add_format(base_format | {'num_format': 'dd/mm/yyyy', 'align': 'centre'})
    }

    # Missing competency names
    if len(diff.missing_competency) > 0:
        header = [{'label': 'Competency Name', 'width': 32}]
        ws_mc = create_report_worksheet(wb, 'Missing Competency', header, formats['header'])
        ws_mc_row = 0
        for competency_name in diff.missing_competency:
            ws_mc_row += 1
            write_cell(ws_mc, ws_mc_row, 0, competency_name, formats['plain'])
        ws_mc.autofilter(0, 0, ws_mc_row, 0)
        ws_mc.set_header('&L&14&A - &D')

    # Extra competency names
    if len(diff.extra_competency) > 0:
        header = [{'label': 'Competency Name', 'width': 32}]
        ws_xc = create_report_worksheet(wb, 'Extra Competency', header, formats['header'])
        ws_xc_row = 0
        for competency_name in diff.extra_competency:
            ws_xc_row += 1
            write_cell(ws_xc, ws_xc_row, 0, competency_name, formats['plain'])
        ws_xc.autofilter(0, 0, ws_xc_row, 0)
        ws_xc.set_header('&L&14&A - &D')

    # Missing staff names
    if len(diff.missing_staff) > 0:
        header = [{'label': 'Staff Name', 'width': 32}]
        ws_ms = create_report_worksheet(wb, 'Missing Staff', header, formats['header'])
        ws_ms_row = 0
        for competency_name in diff.missing_staff:
            ws_ms_row += 1
            write_cell(ws_ms, ws_ms_row, 0, competency_name, formats['plain'])
        ws_ms.autofilter(0, 0, ws_ms_row, 0)
        ws_ms.set_header('&L&14&A - &D')

    # Extra staff names
    if len(diff.extra_staff) > 0:
        header = [{'label': 'Staff Name', 'width': 32}]
        ws_xs = create_report_worksheet(wb, 'Extra Staff', header, formats['header'])
        ws_xs_row = 0
        for competency_name in diff.extra_staff:
            ws_xs_row += 1
            write_cell(ws_xs, ws_xs_row, 0, competency_name, formats['plain'])
        ws_xs.autofilter(0, 0, ws_xs_row, 0)
        ws_xs.set_header('&L&14&A - &D')

    # Missing competencies
    if len(diff.missing_staff_comp) > 0:
        header = [{'label': 'Staff Name', 'width': 32},
                  {'label': 'Competency Name', 'width': 32},
                  {'label': 'Competency Date', 'width': 12}]
        ws_msc = create_report_worksheet(wb, 'Missing Staff Competency', header, formats['header'])
        ws_msc_row = 0
        for competency in diff.missing_staff_comp:
            ws_msc_row += 1
            write_cell(ws_msc, ws_msc_row, 0, competency.staff_name, formats['plain'])
            write_cell(ws_msc, ws_msc_row, 1, competency.competency_name, formats['plain'])
            write_cell(ws_msc, ws_msc_row, 2, competency.competency_date, formats['date'])
        ws_msc.autofilter(0, 0, ws_msc_row, 2)
        ws_msc.set_header('&L&14&A - &D')

    # Extra competencies
    if len(diff.extra_staff_comp) > 0:
        header = [{'label': 'Staff Name', 'width': 32},
                  {'label': 'Competency Name', 'width': 32},
                  {'label': 'Competency Date', 'width': 15}]
        ws_xsc = create_report_worksheet(wb, 'Extra Staff Competency', header, formats['header'])
        ws_xsc_row = 0
        for competency in diff.extra_staff_comp:
            ws_xsc_row += 1
            write_cell(ws_xsc, ws_xsc_row, 0, competency.staff_name, formats['plain'])
            write_cell(ws_xsc, ws_xsc_row, 1, competency.competency_name, formats['plain'])
            write_cell(ws_xsc, ws_xsc_row, 2, competency.competency_date, formats['date'])
        ws_xsc.autofilter(0, 0, ws_xsc_row, 2)
        ws_xsc.set_header('&L&14&A - &D')

    logger.info(f"No competency date changes: {len(diff.staff_comp_date)}")

    wb.close()
    os.startfile(report_path)
