import pytest
from unittest.mock import MagicMock, ANY
from source.excel_functions import yn, write_cell, write_cell_y, write_row, format_status_column, create_report_worksheet


def test_yn():
    assert yn(True) == 'Y'
    assert yn(1) == 'Y'
    assert yn("text") == 'Y'
    assert yn(False) == 'N'
    assert yn(0) == 'N'
    assert yn("") == 'N'
    assert yn(None) == 'N'


def test_write_cell_no_format_no_width():
    ws = MagicMock()
    result = write_cell(ws, 1, 2, "Value")
    
    ws.write.assert_called_once_with(1, 2, "Value")
    ws.set_column.assert_not_called()
    assert result == 3


def test_write_cell_with_format_and_width():
    ws = MagicMock()
    fmt = MagicMock()
    result = write_cell(ws, 5, 0, "Formatted", format=fmt, width=20)
    
    ws.write.assert_called_once_with(5, 0, "Formatted", fmt)
    ws.set_column.assert_called_once_with(0, 0, 20)
    assert result == 1


def test_write_cell_y():
    ws = MagicMock()
    
    # Test True-ish value
    write_cell_y(ws, 1, 1, True)
    ws.write.assert_called_with(1, 1, 'Y')
    
    # Test False-ish value
    write_cell_y(ws, 1, 2, False)
    ws.write.assert_called_with(1, 2, '')


def test_write_row():
    ws = MagicMock()
    formats = {
        'plain': MagicMock(),
        'bold': MagicMock()
    }
    data = [
        {'value': 'Col1'},
        {'value': 'Col2', 'format': 'bold'}
    ]
    
    write_row(ws, 10, data, formats)
    
    assert ws.write.call_count == 2
    ws.write.assert_any_call(10, 0, 'Col1', formats['plain'])
    ws.write.assert_any_call(10, 1, 'Col2', formats['bold'])


def test_format_status_column():
    ws = MagicMock()
    wb = MagicMock()
    # row_status: 0 is header
    # 1: only row with this status (test if row==1 or ... and row==len-1 or ...)
    # 2, 2, 2: group of rows (first, middle, last)
    row_status = [0, 1, 2, 2, 2] 
    status_dict = {
        1: {'colour': '#FF0000', 'title': 'Status 1'},
        2: {'colour': '#00FF00', 'title': 'Status 2'}
    }
    
    # Mock wb.add_format to return a unique object
    wb.add_format.side_effect = lambda d: d
    
    format_status_column(ws, row_status, status_dict, wb)
    
    # We expect 4 rows to be processed (index 1, 2, 3, 4)
    assert ws.write.call_count == 4
    # Check if correct titles were written
    ws.write.assert_any_call(1, 0, 'Status 1', ANY)
    ws.write.assert_any_call(2, 0, 'Status 2', ANY)
    ws.write.assert_any_call(3, 0, 'Status 2', ANY)
    ws.write.assert_any_call(4, 0, 'Status 2', ANY)


def test_create_report_worksheet():
    wb = MagicMock()
    ws = MagicMock()
    wb.add_worksheet.return_value = ws
    
    header = [
        {'label': 'Name', 'width': 30},
        {'label': 'Date', 'width': 15}
    ]
    format_header = MagicMock()
    protect_options = {'objects': True}
    
    result = create_report_worksheet(wb, "Test Sheet", header, format_header, protect_options, "password")
    
    wb.add_worksheet.assert_called_once_with("Test Sheet")
    ws.hide_gridlines.assert_called_once_with(2)
    ws.freeze_panes.assert_called_once_with(1, 0)
    ws.protect.assert_called_once_with("password", protect_options)
    
    assert ws.write.call_count == 2
    ws.write.assert_any_call(0, 0, 'Name', format_header)
    ws.write.assert_any_call(0, 1, 'Date', format_header)
    assert result == ws
