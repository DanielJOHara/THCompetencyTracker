import pytest
from unittest.mock import patch

import logging
import customtkinter as ctk
import _tkinter

from source.role_competency_gui import RoleCompetencyGrid


def pump_events(wnd_root):
    while wnd_root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
        pass


# Set up logging
logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


@pytest.fixture
def ad_with_status(ad):
    """Fixture to add status_dict to the centralized ad fixture."""
    ad.status_dict = {
        0: {'description': 'Out of Date', 'colour': '#FF0000'},
        1: {'description': 'FT Needed', 'colour': '#FFA500'},
        2: {'description': 'Competency Needed', 'colour': '#FFFF00'},
        3: {'description': 'Next Three Months', 'colour': '#00FFFF'},
        4: {'description': 'In Date', 'colour': '#00FF00'},
        5: {'description': 'Not Required', 'colour': '#FFFFFF'},
        6: {'description': 'Not Relevant', 'colour': '#D3D3D3'}
    }
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
def test_role_competency_update(mock_staff_competency_lists, ctk_root, ad_with_status):
    mock_staff_competency_lists.return_value = ([0, 1], [0, 1, 2])
    # Create role competency update window
    wnd_role_competency_update = ctk.CTkToplevel(ctk_root)
    wnd_role_competency_update.grab_set()

    # Populate role competency update window
    # In conftest.py, SC1 has "VoED" (BOTH) and "Cannulation" (RN)
    # So for service "SC1" and staff type "RN", we should have 2 competencies.
    role_competency_grid = RoleCompetencyGrid(ad_with_status, wnd_role_competency_update, "SC1", "RN")
    pump_events(ctk_root)

    assert len(role_competency_grid.chc_rc) == 2
