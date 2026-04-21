import pytest
from unittest.mock import patch

import logging
import customtkinter as ctk
import _tkinter

from source.competency_service_gui import CompetencyServiceGrid, CompetencyServiceUpdate


def pump_events(wnd_root):
    while wnd_root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
        pass


# Set up logging
logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


@pytest.fixture
def mock_ctk_messagebox():
    with patch('source.competency_service_gui.CTkMessagebox') as mock_msgbox:
        mock_msgbox.return_value.get.return_value = 'OK'
        yield mock_msgbox


def test_competency_service_grid(ctk_root, ad, mock_ctk_messagebox):
    # Create grid window
    wnd_cs_grid = ctk.CTkToplevel(ctk_root)
    
    # Populate grid window
    cs_grid = CompetencyServiceGrid(ad, wnd_cs_grid)
    pump_events(ctk_root)
    
    # Check that grid of checkboxes is created
    # conftest has 3 competencies and 3 services
    assert len(cs_grid.chc_cs) == 3
    assert len(cs_grid.chc_cs[0]) == 3
    
    # Test saving: Modify a checkbox
    # VoED (0) - SC3 (2) is unchecked in conftest
    cs_grid.chc_cs[0][2].select()
    cs_grid.handle_save_click()
    pump_events(ctk_root)
    
    mock_ctk_messagebox.assert_called_with(title="Information", message="1 changes saved", icon='info')
    assert ad.md.find_two('Competency Service', 'VoED', 'Competency Name', 'SC3', 'Service Code') > -1

    # Test reset: Modify a checkbox but don't save, then reset
    cs_grid.chc_cs[1][0].deselect()  # Cannulation - SC1 was selected
    cs_grid.handle_reset_click()
    pump_events(ctk_root)
    assert cs_grid.chc_cs[1][0].get() == 1
    
    wnd_cs_grid.destroy()
    pump_events(ctk_root)


def test_competency_service_update(ctk_root, ad, mock_ctk_messagebox):
    # Create update window for a single competency
    wnd_cs_update = ctk.CTkToplevel(ctk_root)
    
    competency_name = 'Phlebotomy'  # index 2
    cs_update = CompetencyServiceUpdate(ad, wnd_cs_update, competency_name)
    pump_events(ctk_root)
    
    # conftest has 3 services
    assert len(cs_update.chc_service_code_list) == 3
    
    # Select SC1 for Phlebotomy
    cs_update.chc_service_code_list[0].select()
    cs_update.handle_save_click()
    pump_events(ctk_root)
    
    mock_ctk_messagebox.assert_called_with(title="Information", message="1 changes saved", icon='info')
    assert ad.md.find_two('Competency Service', competency_name, 'Competency Name', 'SC1', 'Service Code') > -1
    
    # Test delete (deselect all and save)
    cs_update.handle_delete_click()
    pump_events(ctk_root)
    assert ad.md.find_two('Competency Service', competency_name, 'Competency Name', 'SC1', 'Service Code') == -1

    wnd_cs_update.destroy()
    pump_events(ctk_root)
