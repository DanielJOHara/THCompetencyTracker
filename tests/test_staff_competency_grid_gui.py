import pytest
from unittest.mock import patch, MagicMock
import customtkinter as ctk
import tkinter as tk
import _tkinter
from source.staff_competency_grid_gui import StaffCompetencyGrid


def pump_events(wnd_root):
    while wnd_root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
        pass


def test_staff_competency_grid_init(ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    # Use real staff_competency_lists logic
    app = StaffCompetencyGrid(ad_with_status, wnd, "SC1", "RN")
    pump_events(ctk_root)
    
    assert wnd.title() == "Staff Competency Grid"
    assert isinstance(app.cnv_se, tk.Canvas)
    
    # Based on fixture: SC1, RN has John Doe (1 staff)
    # Competency: VoED is BOTH + SC1 + in Role Competency (SC1, R1).
    # Cannulation is RN + SC1 but NOT in Role Competency.
    # So db_c_list should have 1 item (VoED).
    assert len(app.db_s_list) == 1
    assert len(app.db_c_list) == 1
    
    wnd.destroy()
    pump_events(ctk_root)


@patch('source.staff_competency_grid_gui.child_window')
def test_staff_competency_grid_click(mock_child, ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = StaffCompetencyGrid(ad_with_status, wnd, "SC1", "RN")
    pump_events(ctk_root)
    
    # Simulate click on a competency cell (row 0, col 0 in the scrollable grid)
    # In the code it is 'handel_grid_click'
    if hasattr(app, 'lbl_grid') and len(app.lbl_grid) > 0:
        # Mocking an event with widget
        mock_event = MagicMock()
        mock_event.widget = app.lbl_grid[0][0]
        app.handel_grid_click(mock_event)
        assert mock_child.called
    
    wnd.destroy()
    pump_events(ctk_root)
