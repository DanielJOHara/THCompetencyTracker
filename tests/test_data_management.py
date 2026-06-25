import pytest
from unittest.mock import patch, MagicMock
import customtkinter as ctk
import _tkinter
from source.data_management import DataManagement


def pump_events(wnd_root):
    while wnd_root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
        pass


@patch('source.data_management.child_window')
def test_data_management_buttons(mock_child, ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = DataManagement(ad_with_status, wnd)
    pump_events(ctk_root)
    
    # Test a few buttons
    app.btn_service.invoke()
    assert mock_child.called
    
    app.btn_role.invoke()
    assert mock_child.call_count == 2
    
    app.btn_staff.invoke()
    assert mock_child.call_count == 3
    
    wnd.destroy()
    pump_events(ctk_root)
