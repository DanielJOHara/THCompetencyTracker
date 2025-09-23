"""This module provides common functions used to write spreadsheets."""
import xlsxwriter


def yn(value: any) -> str:
    """Return a Y/N string for a value depending on if it is set."""
    if value:
        return 'Y'
    return 'N'


def write_cell_y(ws: xlsxwriter.workbook.Worksheet, row: int, col: int, value: any,
                 format: xlsxwriter.workbook.Format = None, width: int = None) -> int:
    """Function to write Y or blank to a cell depending on passed value evaluating as true and
       increment the column number. If format or width are set they will be used if not they will be ignored."""
    if value:
        local_value = 'Y'
    else:
        local_value = ''
    return write_cell(ws, row, col, local_value, format, width)


def write_cell(ws: xlsxwriter.workbook.Worksheet, row: int, col: int, value: any,
               format: xlsxwriter.workbook.Format = None, width: int = None) -> int:
    """Function to write value to cell and increment the column number.
       If format or width are set they will be used if not they will be ignored."""
    if format:
        ws.write(row, col, value, format)
    else:
        ws.write(row, col, value)

    if width:
        ws.set_column(col, col, width)
    return col + 1
