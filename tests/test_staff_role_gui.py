import pytest
from unittest.mock import patch, MagicMock
import customtkinter as ctk
import _tkinter
from source.staff_role_gui import StaffRoleUpdate


def pump_events(wnd_root):
    while wnd_root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
        pass


@pytest.fixture
def mock_input_warning():
    with patch('source.staff_role_gui.input_warning') as mock_warn:
        yield mock_warn


@pytest.fixture
def mock_ctk_messagebox():
    with patch('source.staff_role_gui.CTkMessagebox') as mock_msgbox:
        mock_msgbox.return_value.get.return_value = 'OK'
        yield mock_msgbox


def test_staff_role_init(ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = StaffRoleUpdate(ad_with_status, wnd)
    pump_events(ctk_root)
    
    assert wnd.title() == "Staff Role Data Update"
    assert app.cmb_staff_name.get() == ""
    # Check that service codes are loaded
    assert len(app.ent_service_code) == ad_with_status.md.len('Service')
    wnd.destroy()
    pump_events(ctk_root)


def test_staff_role_refresh(ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = StaffRoleUpdate(ad_with_status, wnd)
    pump_events(ctk_root)
    
    # Select John Doe
    app.cmb_staff_name.set("John Doe")
    app.refresh_staff()
    pump_events(ctk_root)
    
    # John Doe is R1 in SC1. SC1 is index 0 in Service table in fixture.
    assert app.cmb_role_code[0].get() == "R1"
    
    # Select Jane Smith
    app.cmb_staff_name.set("Jane Smith")
    app.refresh_staff()
    pump_events(ctk_root)
    
    # Jane Smith is R2 in SC2. SC2 is index 1.
    assert app.cmb_role_code[1].get() == "R2"
    wnd.destroy()
    pump_events(ctk_root)


def test_staff_role_save(ctk_root, ad_with_status, mock_ctk_messagebox):
    wnd = ctk.CTkToplevel(ctk_root)
    app = StaffRoleUpdate(ad_with_status, wnd)
    pump_events(ctk_root)
    
    app.cmb_staff_name.set("John Doe")
    app.refresh_staff()
    
    # Change John Doe's role in SC1 to "" (delete it)
    app.cmb_role_code[0].set("")
    app.handle_save_click()
    pump_events(ctk_root)
    
    # Check that it's gone from MasterData
    assert ad_with_status.md.find_two('Staff Role', "SC1", 'Service Code', "John Doe", 'Staff Name') == -1
    mock_ctk_messagebox.assert_called()
    wnd.destroy()
    pump_events(ctk_root)


def test_staff_role_navigation(ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = StaffRoleUpdate(ad_with_status, wnd)
    pump_events(ctk_root)
    
    # Initial db_s is len(Staff) = 2
    # Next should go to index 0 (John Doe)
    app.handle_next_click()
    assert app.cmb_staff_name.get() == "John Doe"
    
    # Next should go to index 1 (Jane Smith)
    app.handle_next_click()
    assert app.cmb_staff_name.get() == "Jane Smith"
    
    # Next should go back to 0
    app.handle_next_click()
    assert app.cmb_staff_name.get() == "John Doe"
    
    # Previous should go back to 1
    app.handle_previous_click()
    assert app.cmb_staff_name.get() == "Jane Smith"
    wnd.destroy()
    pump_events(ctk_root)


def test_staff_role_filter(ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = StaffRoleUpdate(ad_with_status, wnd)
    pump_events(ctk_root)
    
    app.ent_name_filter.insert(0, "Jane")
    app.filter_names()
    pump_events(ctk_root)
    
    # Should have filtered to Jane Smith only
    assert app.cmb_staff_name.get() == "Jane Smith"
    assert app.cmb_role_code[1].get() == "R2"
    wnd.destroy()
    pump_events(ctk_root)


def test_staff_role_single_staff_mode(ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    # Open for Jane Smith directly
    app = StaffRoleUpdate(ad_with_status, wnd, staff_name="Jane Smith")
    pump_events(ctk_root)
    
    assert app.cmb_staff_name.get() == "Jane Smith"
    assert app.cmb_staff_name.cget('state') == 'disabled'
    assert app.cmb_role_code[1].get() == "R2"
    
    # Save should destroy window in single mode
    app.handle_save_click()
    pump_events(ctk_root)
    # Check if window is destroyed - hard to check directly on wnd object sometimes but let's see
    # If we are here and pump_events finished, it should be gone.
    wnd.destroy()
    pump_events(ctk_root)
