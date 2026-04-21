import pytest
from unittest.mock import patch

import logging
import customtkinter as ctk
import _tkinter

from source.role_service_gui import RoleServiceGrid, RoleServiceUpdate


def pump_events(wnd_root):
    while wnd_root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
        pass


# Set up logging
logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


@pytest.fixture
def mock_ctk_messagebox():
    with patch('source.role_service_gui.CTkMessagebox') as mock_msgbox:
        mock_msgbox.return_value.get.return_value = 'OK'
        yield mock_msgbox

def test_role_service_grid(ctk_root, ad, mock_ctk_messagebox):
    # Create grid window
    wnd_rs_grid = ctk.CTkToplevel(ctk_root)
    
    # Populate grid window
    rs_grid = RoleServiceGrid(ad, wnd_rs_grid)
    pump_events(ctk_root)
    
    # Check that grid of checkboxes is created
    # conftest has 2 roles and 3 services
    assert len(rs_grid.chc_cs) == 2
    assert len(rs_grid.chc_cs[0]) == 3
    
    # Test saving: Modify a checkbox
    # R1 (0) - SC2 (1) is unchecked in conftest
    rs_grid.chc_cs[0][1].select()
    rs_grid.handle_save_click()
    pump_events(ctk_root)
    
    mock_ctk_messagebox.assert_called_with(title="Information", message="1 changes saved", icon='info')
    assert ad.md.find_two('Role Service', 'R1', 'Role Code', 'SC2', 'Service Code') > -1

    # Test reset: Modify a checkbox but don't save, then reset
    rs_grid.chc_cs[0][0].deselect() # R1 - SC1 was selected
    rs_grid.handle_reset_click()
    pump_events(ctk_root)
    assert rs_grid.chc_cs[0][0].get() == 1
    
    wnd_rs_grid.destroy()
    pump_events(ctk_root)

def test_role_service_update(ctk_root, ad, mock_ctk_messagebox):
    # Create update window for a single role
    wnd_rs_update = ctk.CTkToplevel(ctk_root)
    
    role_code = 'R1'
    rs_update = RoleServiceUpdate(ad, wnd_rs_update, role_code)
    pump_events(ctk_root)
    
    # conftest has 3 services
    assert len(rs_update.chc_service_code_list) == 3
    
    # Select SC2 for R1
    rs_update.chc_service_code_list[1].select()
    rs_update.handle_save_click()
    pump_events(ctk_root)
    
    mock_ctk_messagebox.assert_called_with(title="Information", message="1 changes saved", icon='info')
    assert ad.md.find_two('Role Service', role_code, 'Role Code', 'SC2', 'Service Code') > -1
    
    # Test delete (deselect all and save)
    rs_update.handle_delete_click()
    pump_events(ctk_root)
    # Check that all associations for R1 are gone (SC1 was there)
    assert ad.md.find_two('Role Service', role_code, 'Role Code', 'SC1', 'Service Code') == -1
    assert ad.md.find_two('Role Service', role_code, 'Role Code', 'SC2', 'Service Code') == -1

    wnd_rs_update.destroy()
    pump_events(ctk_root)
