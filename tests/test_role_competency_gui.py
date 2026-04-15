import pytest
from unittest.mock import patch

import logging
import customtkinter as ctk
import _tkinter

from source.master_data import MasterData
from source.appdata import AppData
from source.role_competency_gui import RoleCompetencyGrid


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
    ad.status_dict = {
        0: {'description': 'Out of Date', 'colour': '#FF0000'},
        1: {'description': 'FT Needed', 'colour': '#FFA500'},
        2: {'description': 'Competency Needed', 'colour': '#FFFF00'},
        3: {'description': 'Next Three Months', 'colour': '#00FFFF'},
        4: {'description': 'In Date', 'colour': '#00FF00'},
        5: {'description': 'Not Required', 'colour': '#FFFFFF'},
        6: {'description': 'Not Relevant', 'colour': '#D3D3D3'}
    }
    ad.md = MasterData('None', 30)
    ad.md.add_table('Service', ['Service Code', 'Service Name'], [["SER", "Service"]])
    ad.md.add_table('Staff',
                    ['Staff Name'],
                    [["Staff One"], ["Staff Two"], ["Staff Three"]])
    ad.md.add_table('Role',
                    ['Role Code', 'Role Name', 'RN', 'Display Order'],
                    [["RC1", "Role Code One", 1, 1],
                     ["RC2", 'Role Code Two', 1, 2],
                     ["RC3", "Role Code Three", 0, 3]])
    ad.md.add_table('Competency',
                    ['Competency Name', 'Display Order', 'Service Code',
                     'Scope', 'Expiry', 'Prerequisite', 'Nightshift', 'Bank'],
                    [["Competency One", 1, '', "BOTH", 2, "", True, True],
                     ["Competency Two", 2, '', "RN", 2, "", False, True],
                     ["Competency Three", 3, '', "HCA", 2, "", True, False]])
    ad.md.add_table('Role Competency',
                    ['Service Code', 'Role Code', 'Competency Name'],
                    [["SER", "RC1", "Competency One"],
                     ["SER", "RC2", "Competency Two"],
                     ["SER", "RC3", "Competency Three"]])
    ad.md.add_table('Staff Role',
                    ['Staff Name', 'Role Code', 'Service Code'],
                    [["Staff One", "RC1", "SEV"],
                     ["Staff Two", "RC2", "SEV"],
                     ["Staff Three", "RC3", "SEV"]])
    ad.md.add_table('Staff Competency',
                    ['Staff Name', 'Competency Name', 'Competency Date', 'Prerequisite Date',
                     'Notes', 'Required', 'Not Required', 'Completed', 'Achieved'],
                    [["Staff One", "Competency One", None, None, "", False, False, False, False],
                     ["Staff Two", "Competency One", None, None, "", False, False, False, False],
                     ["Staff Three", "Competency Two", None, None, "", False, False, False, False]])

    def finalizer():
        # No file to unlock as MasterData is mocked with 'None'
        pass

    request.addfinalizer(finalizer)
    return ad


@pytest.fixture
def mock_input_warning():
    with patch('source.role_competency_gui.input_warning') as mock_warn:
        yield mock_warn


@pytest.fixture
def mock_ctk_messagebox():
    with patch('source.role_competency_gui.CTkMessagebox') as mock_msgbox:
        yield mock_msgbox


@patch('source.role_competency_gui.staff_competency_lists')
def test_role_competency_update(mock_staff_competency_lists, ctk_root, ad):
    mock_staff_competency_lists.return_value = ([0, 1], [0, 1, 2])
    # Create role competency update window
    wnd_role_competency_update = ctk.CTkToplevel(ctk_root)
    wnd_role_competency_update.grab_set()

    # Populate role competency update window
    role_competency_grid = RoleCompetencyGrid(ad, wnd_role_competency_update, "SER", "RN")
    pump_events(ctk_root)

    assert len(role_competency_grid.chc_rc) == 2
