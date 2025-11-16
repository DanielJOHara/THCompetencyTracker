"""This module defines the ToolTip class which can be used to add roll over text to a widget."""
import logging
import tkinter as tk

from source.appdata import AppData
from source.competency_display import set_competency_status

logger = logging.getLogger(__name__)


class ToolTip(object):
    def __init__(self, widget, tip_text: str, x_offset=10, y_offset=10) -> None:
        self.widget = widget
        self.tip_text = tip_text
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.tip_window = None

        self.widget.bind('<Enter>', self.show_tip)
        self.widget.bind('<Leave>', self.hide_tip)

    def show_tip(self, event):
        """Display text in tooltip window"""
        logger.debug(f"show_tip call with event: {event}")
        if self.tip_window or not self.tip_text:
            return

        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + self.x_offset
        y = y + cy + self.widget.winfo_rooty() + self.y_offset

        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tip_window,
                         text=self.tip_text,
                         justify=tk.LEFT,
                         background="#ffffe0",
                         relief=tk.SOLID,
                         borderwidth=1,
                         font=('Lucida Console', 13, "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event):
        """Remove tool tip window"""
        logger.debug(f"hide_tip call with event: {event}")
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


def competency_tip_text(ad: AppData, db_c: int, db_s_list: list[int], service_code: str, staff_type: str) -> str:
    """Function to set tool tip text for a competency."""
    competency_name = ad.md.get('Competency', 'Competency Name', db_c)
    scope = ad.md.get('Competency', 'Scope', db_c)
    display_order = ad.md.get('Competency', 'Display Order', db_c)
    expiry = ad.md.get('Competency', 'Expiry', db_c)
    prerequisite = ad.md.get('Competency', 'Prerequisite', db_c)
    nightshift = ad.md.get('Competency', 'Nightshift', db_c)
    bank = ad.md.get('Competency', 'Bank', db_c)

    tip_text = (f"Competency Name : {competency_name}\n"
                f"Scope           : {scope}\n"
                f"Display Order   : {display_order}\n"
                f"Expiry          : {expiry}\n"
                f"Prerequisite    : {yes_no(prerequisite)}\n"
                f"Nightshift      : {yes_no(nightshift)}\n"
                f"Bank            : {yes_no(bank)}\n\n"
                f"Number of {staff_type}s : {len(db_s_list)}\n")

    status_list = [0] * len(ad.status_dict)
    for db_s in db_s_list:
        status = set_competency_status(ad, db_s, db_c, [service_code])
        status_list[status] += 1

    for status in range(len(ad.status_dict)):
        tip_text += f"{ad.status_dict[status]["description"] : >18} : {status_list[status]}\n"

    return tip_text


def role_tip_text(ad: AppData, db_r: int, service_code: str) -> str:
    """Function to set tool tip code for a role."""
    role_code = ad.md.get('Role', 'Role Code', db_r)
    role_name = ad.md.get('Role', 'Role Name', db_r)
    display_order = ad.md.get('Role', 'Display Order', db_r)
    rn = ad.md.get('Role', 'RN', db_r)
    role_count = ad.md.count_two('Staff Role', 'Service Code', service_code, 'Role Code', role_code)

    tip_text = (f"Role Code     : {role_code}\n"
                f"Role Name     : {role_name}\n"
                f"Display Order : {display_order}\n"
                f"RN            : {yes_no(rn)}\n"
                f"Role Count    : {role_count}")

    return tip_text


def yes_no(value: any) -> str:
    """Return a Yes/No string for a value depending on if it is set."""
    if value:
        return 'Yes'
    return 'No'
