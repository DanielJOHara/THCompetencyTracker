"""This module provides common functions used to write spreadsheets."""
import xlsxwriter
from typing import Any


def yn(value: Any) -> str:
    """Return a Y/N string for a value depending on if it is set."""
    if value:
        return 'Y'
    return 'N'


def write_cell_y(ws: xlsxwriter.workbook.Worksheet,
                 row: int,
                 col: int,
                 value: Any,
                 format: xlsxwriter.workbook.Format | None = None,
                 width: int | None = None) -> int:
    """Function to write Y or blank to a cell depending on passed value evaluating as true and
       increment the column number. If format or width are set they will be used if not they will be ignored."""
    if value:
        local_value = 'Y'
    else:
        local_value = ''
    return write_cell(ws, row, col, local_value, format, width)


def write_cell(ws: xlsxwriter.workbook.Worksheet,
               row: int,
               col: int,
               value: Any,
               format: xlsxwriter.workbook.Format | None = None,
               width: int | None = None) -> int:
    """Function to write value to cell and increment the column number.
       If format or width are set they will be used if not they will be ignored."""
    if format:
        ws.write(row, col, value, format)
    else:
        ws.write(row, col, value)

    if width:
        ws.set_column(col, col, width)
    return col + 1


def write_row(ws: xlsxwriter.workbook.Worksheet, row: int, data: list, formats: dict):
    """Write a row of data to a worksheet."""
    col = 0
    for item in data:
        if 'format' in item:
            col = write_cell(ws, row, col, item['value'], formats[item['format']])
        else:
            col = write_cell(ws, row, col, item['value'], formats['plain'])


def format_status_column(ws: xlsxwriter.workbook.Worksheet,
                         row_status: list[int],
                         status_dict: dict,
                         wb: xlsxwriter.workbook.Workbook):
    """Format the status column of a worksheet."""
    for row in range(1, len(row_status)):
        status_colour = status_dict[row_status[row]]['colour']
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

        write_cell(ws, row, 0, status_dict[row_status[row]]['description'], this_format)


def create_report_worksheet(wb: xlsxwriter.workbook.Workbook,
                            sheet_name: str,
                            header: list,
                            format_header: xlsxwriter.workbook.Format,
                            protect_options: dict,
                            password: str) -> xlsxwriter.workbook.Worksheet:
    """Create a worksheet with a header row and basic formatting."""
    ws = wb.add_worksheet(sheet_name)
    ws.hide_gridlines(2)
    ws.freeze_panes(1, 0)
    col = 0
    for item in header:
        col = write_cell(ws, 0, col, item['label'], format_header, width=item['width'])
    ws.protect(password, protect_options)
    return ws
