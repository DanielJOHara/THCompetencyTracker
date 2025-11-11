"""This module provides common functions used by the GUI windows."""
import datetime
import logging
from typing import Any, Callable, Union

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from source.appdata import AppData

logger = logging.getLogger(__name__)


def child_window(function: Callable[..., Any], ad: AppData,
                 wnd_parent: Union[ctk.CTk, ctk.CTkToplevel], *args, **kwargs) -> None:
    """Function to create a child window"""
    # Create child window object
    wnd_child = ctk.CTkToplevel()
    wnd_child.grab_set()

    # Change window icon
    if ad.wnd_root:
        wnd_child.wm_iconbitmap()
        wnd_child.after(300, lambda: wnd_child.iconphoto(False, ad.wnd_root.iconpath))

    # Call supplied function or class for window
    function(ad, wnd_child, *args, **kwargs)

    if wnd_parent and (not ad.args.readonly or wnd_parent != ad.wnd_root):
        # Set parent window cursor to watch (busy circle) then wait for child window to exit
        wnd_parent.config(cursor="watch")
        wnd_parent.wait_window(wnd_child)

        # Reset parent window cursor and return focus to parent window
        wnd_parent.config(cursor="")
        wnd_parent.grab_set()


def input_warning(wnd: Union[ctk.CTk, ctk.CTkToplevel], message: str) -> None:
    """Display a warning message box then grab back focus."""
    win_msg = CTkMessagebox(title="Data Input Error", message=message, icon='warning', option_1='OK')
    logger.info(f"Displaying Data Input Error: {message}")
    if win_msg.get() != 'OK':
        pass
    wnd.grab_set()


def set_disabled_entry(ent: ctk.CTkEntry, string: str) -> None:
    """Set a disabled Entry widget to the supplies string."""
    ent.configure(state='normal')
    ent.delete(0, 9999)
    ent.insert(0, str(string))
    ent.configure(state='disabled')


def set_disabled_checkbox(chc: ctk.CTkCheckBox, value: any) -> None:
    """Set a disabled CheckBox widget to the supplies value."""
    chc.configure(state='normal')
    if value:
        chc.select()
    else:
        chc.deselect()
    chc.configure(state='disabled')


def date_to_string(date: Union[datetime.date, datetime.datetime]) -> str:
    """Converts a datetime to the standard format used by this application."""
    if isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
        return date.strftime('%d.%m.%y')
    return ''


def parse_date(text: str) -> Union[str, datetime.date]:
    """Converts multiple text date formats to a datetime date."""
    for fmt in ('%d.%m.%y', '%d-%m-%y', '%d/%m/%y',
                '%d.%m.%Y', '%d-%m-%Y', '%d/%m/%Y',
                '%Y.%m.%d', '%Y-%m-%d', '%Y/%m/%d'):
        try:
            return datetime.datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            pass
    return ''


def widget_dict_values(widget_dict_list: list) -> list:
    """Get the values for a list of widget dictionaries and return values as a list of dictionaries."""
    value_dict_list = []
    for widget_dict in widget_dict_list:
        value_dict = {}
        for widget in widget_dict:
            value_dict[widget] = widget_dict[widget].get()
        value_dict_list.append(value_dict)

    return value_dict_list


def widget_list_values(widget_list: list) -> list:
    """Get the values for a list of widgets and return as a list of values."""
    value_list = []
    for widget in widget_list:
        value_list.append(widget.get())

    return value_list
