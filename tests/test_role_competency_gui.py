import pytest
from unittest.mock import patch, MagicMock

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
def mock_ctk_messagebox():
    with patch('source.role_competency_gui.CTkMessagebox') as mock_msgbox:
        mock_msgbox.return_value.get.return_value = 'OK'
        yield mock_msgbox


def test_role_competency_grid_init(ctk_root, ad_with_status):
    # Create role competency update window
    wnd_role_competency_update = ctk.CTkToplevel(ctk_root)

    # Populate role competency update window
    # In conftest.py, SC1 has "VoED" (BOTH) and "Cannulation" (RN)
    # So for service "SC1" and staff type "RN", we should have 2 competencies.
    role_competency_grid = RoleCompetencyGrid(ad_with_status, wnd_role_competency_update, "SC1", "RN")
    pump_events(ctk_root)

    assert len(role_competency_grid.chc_rc) == 2
    assert len(role_competency_grid.chc_rc[0]) == len(role_competency_grid.db_r_list)

    # Close role competency update window
    wnd_role_competency_update.destroy()
    pump_events(ctk_root)


def test_role_competency_save(ctk_root, ad_with_status, mock_ctk_messagebox):
    wnd = ctk.CTkToplevel(ctk_root)
    app = RoleCompetencyGrid(ad_with_status, wnd, "SC1", "RN")
    pump_events(ctk_root)

    # Modify a checkbox: SC1, RN=R1 (index 0), Competency=VoED (index 0)
    # VoED (0) - SC1 - R1 (0) is selected in conftest.py
    app.chc_rc[0][0].deselect()
    app.handle_save_click()
    pump_events(ctk_root)

    mock_ctk_messagebox.assert_called()
    # Should be gone from MasterData
    assert ad_with_status.md.find_three('Role Competency', 'SC1', 'Service Code', 'R1', 'Role Code', 'VoED', 'Competency Name') == -1

    wnd.destroy()
    pump_events(ctk_root)


def test_role_competency_reset(ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = RoleCompetencyGrid(ad_with_status, wnd, "SC1", "RN")
    pump_events(ctk_root)

    # Modify a checkbox but don't save
    app.chc_rc[0][0].deselect()
    assert app.chc_rc[0][0].get() == 0

    # Reset
    app.handle_reset_click()
    pump_events(ctk_root)

    # Should be selected again
    assert app.chc_rc[0][0].get() == 1

    wnd.destroy()
    pump_events(ctk_root)
