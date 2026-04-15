import pytest
from unittest.mock import patch

import logging
import customtkinter as ctk
import _tkinter

from source.master_data import MasterData
from source.appdata import AppData
from source.competency_gui import CompetencyAdd, CompetencyDelete, CompetencyUpdate


def pump_events(wnd_root):
    while wnd_root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
        pass


# Set up logging
logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


@pytest.fixture(scope="module")
def ctk_root():
    try:
        root = ctk.CTk()
        yield root
        root.destroy()
    except _tkinter.TclError:
        pytest.skip("Skipping GUI tests: No display available")


@pytest.fixture
def ad(request):
    """Fixture to create an AppData object with a MasterData instance."""
    ad = AppData()
    ad.md = MasterData('None', 30)
    ad.md.add_table('Competency',
                    ['Competency Name', 'Display Order', 'Service Code', 'Scope', 'Expiry', 'Prerequisite', 'Nightshift', 'Bank'],
                    [["VoED", 1, '', "BOTH", 2, 0, 0, 0],
                     ["Cannulation", 2, '', "RN", 0, 0, 0, 0],
                     ["Phlebotomy", 3, '', "HCA", 2, 0, 0, 0]])
    ad.md.add_table('Role Competency',
                    ['Service Code', 'Role Code', 'Competency Name'],
                    [["IPS", "SN", "VoED"]])
    ad.md.add_table('Staff Competency',
                    ['Staff Name', 'Competency Name'],
                    [["John Doe", "VoED"]])
    ad.md.add_table('Service',
                    ['Service Name', 'Service Code'],
                    [["Service 1", "s1"]])
    yield ad


@pytest.fixture
def mock_input_warning():
    with patch('source.competency_gui.input_warning') as mock_warn:
        yield mock_warn


@pytest.fixture
def mock_ctk_messagebox():
    with patch('source.competency_gui.CTkMessagebox') as mock_msgbox:
        yield mock_msgbox


def test_competency_update(ctk_root, ad):
    # Create competency update window
    wnd_competency_update = ctk.CTkToplevel(ctk_root)
    wnd_competency_update.grab_set()

    # Populate competency update window
    competency_update = CompetencyUpdate(ad, wnd_competency_update)
    pump_events(ctk_root)

    assert len(competency_update.competency_widgets) == ad.md.len('Competency')

    # Test saving changes
    competency_update.competency_widgets[0]['Competency Name'].delete(0, 9999)
    competency_update.competency_widgets[0]['Competency Name'].insert(0, "New VoED")
    competency_update.handle_save_click()
    pump_events(ctk_root)
    assert ad.md.get('Competency', 'Competency Name', 0) == "New VoED"


def test_competency_add(ctk_root, mock_input_warning, mock_ctk_messagebox, ad):
    # Create competency add window
    wnd_competency_add = ctk.CTkToplevel(ctk_root)
    wnd_competency_add.grab_set()

    # Populate competency add window
    competency_add = CompetencyAdd(ad, wnd_competency_add)
    pump_events(ctk_root)

    # Blank input test
    competency_add.ent_competency_name.delete(0, 9999)
    competency_add.ent_display_order.delete(0, 9999)
    competency_add.handle_add_click()
    pump_events(ctk_root)
    mock_input_warning.assert_called_with(competency_add.wnd_competency_add, "Competency Name field must be set!")

    # Add new competency
    competency_add.ent_competency_name.delete(0, 9999)
    competency_add.ent_competency_name.insert(0, 'New Competency')
    competency_add.cmb_scope.set('BOTH')
    competency_add.ent_display_order.delete(0, 9999)
    competency_add.ent_display_order.insert(0, '4')
    competency_add.ent_expiry.delete(0, 9999)
    competency_add.ent_expiry.insert(0, '365')
    competency_add.chc_prerequisite.select()
    competency_add.btn_add.invoke()
    pump_events(ctk_root)

    # Check information message call
    mock_ctk_messagebox.assert_called_once_with(title='Information', message='Added New Competency', icon='info')

    # Find the new record
    db_c = ad.md.find_one('Competency', 'New Competency', 'Competency Name')
    assert db_c > -1
    assert ad.md.get('Competency', 'Scope', db_c) == 'BOTH'

    # Close competency add window
    competency_add.btn_exit.invoke()
    pump_events(ctk_root)


def test_competency_delete(ctk_root, ad):
    # Create competency delete window
    wnd_competency_delete = ctk.CTkToplevel(ctk_root)
    wnd_competency_delete.grab_set()

    # Populate competency delete window
    competency_delete = CompetencyDelete(ad, wnd_competency_delete)
    pump_events(ctk_root)

    # Select the competency record and check the name updates correctly
    competency_delete.cmb_competency_name.set('Cannulation')
    competency_delete.refresh_competency('None')
    pump_events(ctk_root)
    assert competency_delete.ent_scope.get() == 'RN'

    # Delete the record
    competency_delete.btn_delete.invoke()
    pump_events(ctk_root)
    assert competency_delete.cmb_competency_name.get() == ''
    assert "Cannulation" not in competency_delete.cmb_competency_name.cget("values")
    assert ad.md.find_one('Competency', 'Cannulation', 'Competency Name') == -1
    assert ad.md.len("Competency") == 2

    competency_delete.btn_exit.invoke()
    pump_events(ctk_root)
