import datetime
import pytest
from unittest.mock import MagicMock, patch
import customtkinter as ctk
import _tkinter

from source.window import (
    child_window,
    input_warning,
    set_disabled_entry,
    set_disabled_checkbox,
    date_to_string,
    parse_date,
    show_master_data_error,
    widget_dict_values,
    widget_list_values,
    widget_2d_list_values,
    staff_name_filter,
    staff_name_title_case
)


def pump_events(wnd_root):
    while wnd_root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
        pass


def test_date_to_string():
    dt = datetime.date(2023, 10, 5)
    assert date_to_string(dt) == "05.10.23"
    
    dt_full = datetime.datetime(2023, 10, 5, 12, 0)
    assert date_to_string(dt_full) == "05.10.23"
    
    assert date_to_string("not a date") == ""
    assert date_to_string(None) == ""


def test_parse_date():
    expected = datetime.date(2023, 10, 5)
    assert parse_date("05.10.23") == expected
    assert parse_date("05-10-23") == expected
    assert parse_date("05/10/23") == expected
    assert parse_date("05.10.2023") == expected
    assert parse_date("2023-10-05") == expected
    assert parse_date("invalid") == ""


def test_widget_list_values():
    mock1 = MagicMock()
    mock1.get.return_value = "val1"
    mock2 = MagicMock()
    mock2.get.return_value = "val2"
    
    assert widget_list_values([mock1, mock2]) == ["val1", "val2"]


def test_widget_2d_list_values():
    mock1 = MagicMock()
    mock1.get.return_value = "a"
    mock2 = MagicMock()
    mock2.get.return_value = "b"
    mock3 = MagicMock()
    mock3.get.return_value = "c"
    
    input_list = [[mock1, mock2], [mock3]]
    assert widget_2d_list_values(input_list) == [["a", "b"], ["c"]]


def test_set_disabled_entry(ctk_root):
    ent = ctk.CTkEntry(ctk_root)
    ent.configure(state='disabled')
    set_disabled_entry(ent, "New Value")
    assert ent.get() == "New Value"
    assert ent.cget('state') == 'disabled'


def test_set_disabled_checkbox(ctk_root):
    chc = ctk.CTkCheckBox(ctk_root)
    chc.configure(state='disabled')
    set_disabled_checkbox(chc, True)
    assert chc.get() == 1
    assert chc.cget('state') == 'disabled'
    
    set_disabled_checkbox(chc, False)
    assert chc.get() == 0
    assert chc.cget('state') == 'disabled'


@patch('source.window.CTkMessagebox')
def test_input_warning(mock_mb, ctk_root):
    # Case 1: get() == 'OK'
    mock_mb.return_value.get.return_value = 'OK'
    wnd = MagicMock()
    input_warning(wnd, "Warning Message")
    mock_mb.assert_called_with(title="Data Input Error", message="Warning Message", icon='warning', option_1='OK')
    wnd.grab_set.assert_called_once()
    
    # Case 2: get() != 'OK'
    mock_mb.return_value.get.return_value = 'CANCEL'
    input_warning(wnd, "Warning Message")
    assert mock_mb.call_count == 2


def test_widget_dict_values(ctk_root):
    ent = ctk.CTkEntry(ctk_root)
    ent.insert(0, "val1")
    cmb = ctk.CTkComboBox(ctk_root, values=["val2"])
    cmb.set("val2")
    
    input_list = [{"key1": ent, "key2": cmb}]
    result = widget_dict_values(input_list)
    assert result == [{"key1": "val1", "key2": "val2"}]


@patch('source.window.ctk.CTkTextbox')
@patch('source.window.ctk.CTkToplevel')
def test_show_master_data_error(mock_toplevel, ctk_root):
    mock_wnd = MagicMock()
    mock_toplevel.return_value = mock_wnd

    parent = MagicMock()
    show_master_data_error("Error Text", wnd_parent=parent)
    mock_toplevel.assert_called_once()
    parent.wait_window.assert_called_once_with(mock_wnd)


def test_child_window_basic(ctk_root, ad):
    mock_func = MagicMock()
    parent = MagicMock()
    ad.wnd_root = MagicMock()
    ad.wnd_root.iconpath = "path/to/icon"
    
    with patch('source.window.ctk.CTkToplevel') as mock_toplevel:
        mock_child = MagicMock()
        mock_toplevel.return_value = mock_child
        
        child_window(mock_func, ad, parent, "arg1", kw="kw1")
        
        mock_func.assert_called_once_with(ad, mock_child, "arg1", kw="kw1")
        mock_child.grab_set.assert_called_once()
        mock_child.wm_iconbitmap.assert_called_once()
        mock_child.after.assert_called_once()
        
        # To test the lambda in after:
        args, kwargs = mock_child.after.call_args
        callback = args[1]
        callback()
        mock_child.iconphoto.assert_called_once_with(False, ad.wnd_root.iconpath)
        
        parent.wait_window.assert_called_once_with(mock_child)


def test_staff_name_filter():
    assert staff_name_filter("John Doe") == "John Doe"
    assert staff_name_filter("  John  Doe  ") == "John Doe"
    assert staff_name_filter("John-Doe") == "John-Doe"
    assert staff_name_filter("O'Reilly") == "O'Reilly"
    assert staff_name_filter("John Doe 123!") == "John Doe"
    assert staff_name_filter("John   Doe") == "John Doe"
    assert staff_name_filter("") == ""


def test_staff_name_title_case():
    assert staff_name_title_case("john doe") == "John Doe"
    assert staff_name_title_case("JOHN DOE") == "John Doe"
    assert staff_name_title_case("jOHN dOE") == "John Doe"
    assert staff_name_title_case("  john   doe  ") == "John Doe"
    assert staff_name_title_case("john-doe") == "John-Doe"
    assert staff_name_title_case("o'reilly") == "O'Reilly"
    assert staff_name_title_case("john doe 123!") == "John Doe"
