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
    ad.md.add_table('Role',
                    ['Role Code', 'Role Name', 'RN', 'Display Order'],
                    [["RC1", "Role Code One", 0, 1],
                     ["RC2", 'Role Code Two', 1, 2],
                     ["RC3", "Role Code Three", 0, 3]])
    ad.md.add_table('Competency',
                    ['Competency Code', 'Competency Name', 'Display Order',
                     'Scope', 'Expiry', 'Prerequisite', 'Nightshift', 'Bank'],
                    [["C1", "Competency One", 1, "ST1", 12, "", True, True],
                     ["C2", "Competency Two", 2, "ST1", 12, "", False, True],
                     ["C3", "Competency Three", 3, "ST2", 12, "", True, False]])
    ad.md.add_table('Staff',
                    ['Staff Code', 'Staff Name', 'Service', 'Staff Type'],
                    [["S1", "Staff One", "SER", "ST1"],
                     ["S2", "Staff Two", "SER", "ST1"],
                     ["S3", "Staff Three", "SER", "ST2"]])
    ad.md.add_table('Staff Role',
                    ['Staff', 'Role'],
                    [["S1", "RC1"],
                     ["S2", "RC2"],
                     ["S3", "RC3"]])
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
    role_competency_grid = RoleCompetencyGrid(ad, wnd_role_competency_update, "SER", "ST1")
    pump_events(ctk_root)

    assert len(role_competency_grid.chc_rc) == 3
