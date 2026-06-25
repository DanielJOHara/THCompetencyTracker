import pytest
from unittest.mock import patch, MagicMock
import customtkinter as ctk
import _tkinter
from source.choose_colours_gui import ChooseColours, colour_to_numbers


def pump_events(wnd_root):
    while wnd_root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
        pass


def test_colour_to_numbers():
    assert colour_to_numbers("#FFFFFF") == "255 255 255"
    assert colour_to_numbers("#000000") == "0 0 0"
    assert colour_to_numbers("invalid") == ""


def test_choose_colours_init(ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = ChooseColours(ad_with_status, wnd)
    pump_events(ctk_root)
    
    assert wnd.title() == "Competency Status Colour Chooser"
    assert len(app.btn_current) == len(ad_with_status.status_dict)
    wnd.destroy()
    pump_events(ctk_root)


@patch('source.choose_colours_gui.colorchooser.askcolor')
def test_colour_chooser(mock_askcolor, ctk_root, ad_with_status):
    mock_askcolor.return_value = ((255, 0, 0), "#FF0000")
    
    wnd = ctk.CTkToplevel(ctk_root)
    app = ChooseColours(ad_with_status, wnd)
    pump_events(ctk_root)
    
    # Trigger colour chooser for first status
    app.colour_chooser(0)
    
    assert ad_with_status.status_dict[0]['colour'] == "#FF0000"
    wnd.destroy()
    pump_events(ctk_root)


def test_reset_defaults(ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = ChooseColours(ad_with_status, wnd)
    pump_events(ctk_root)
    
    # Change a colour
    ad_with_status.status_dict[0]['colour'] = "#000000"
    
    app.reset_defaults()
    
    assert ad_with_status.status_dict[0]['colour'] == ad_with_status.status_dict[0]['default']
    wnd.destroy()
    pump_events(ctk_root)
