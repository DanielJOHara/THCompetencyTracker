import pytest
from unittest.mock import patch, MagicMock
import customtkinter as ctk
import _tkinter
from source.staff_competency_gui import StaffCompetencyUpdate


def pump_events(wnd_root):
    while wnd_root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
        pass


@pytest.fixture
def mock_input_warning():
    with patch('source.staff_competency_gui.input_warning') as mock_warn:
        yield mock_warn


@pytest.fixture
def mock_ctk_messagebox():
    with patch('source.staff_competency_gui.CTkMessagebox') as mock_msgbox:
        mock_msgbox.return_value.get.return_value = 'OK'
        yield mock_msgbox


def test_staff_competency_update_single_mode(ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    # John Doe has VoED record in Staff Competency in fixture
    app = StaffCompetencyUpdate(ad_with_status, wnd, "John Doe", "VoED")
    pump_events(ctk_root)
    
    assert app.ent_staff_name.get() == "John Doe"
    assert app.ent_competency_name.get() == "VoED"
    assert app.chc_achieved.get() == 1
    
    wnd.destroy()
    pump_events(ctk_root)


def test_staff_competency_update_multi_mode(ctk_root, ad_with_status, mock_ctk_messagebox):
    wnd = ctk.CTkToplevel(ctk_root)
    app = StaffCompetencyUpdate(ad_with_status, wnd)
    pump_events(ctk_root)
    
    app.cmb_staff_name.set("Jane Smith")
    app.cmb_competency_name.set("Phlebotomy")
    app.refresh_competency()
    pump_events(ctk_root)
    
    # Phlebotomy for Jane Smith is not in Staff Competency fixture, so fields should be blank/off
    assert app.chc_achieved.get() == 0
    
    # Set achieved and save
    app.chc_achieved.select()
    app.handle_save_click()
    pump_events(ctk_root)
    
    # Verify it was added to MasterData
    assert ad_with_status.md.find_two('Staff Competency', "Jane Smith", 'Staff Name', "Phlebotomy", 'Competency Name') > -1
    
    wnd.destroy()
    pump_events(ctk_root)
