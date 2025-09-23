"""Module contains window to allow users to change colours used for the different competency statuses."""
import logging

import customtkinter as ctk
from tkinter import colorchooser

from source.appdata import AppData

logger = logging.getLogger(__name__)


class ChooseColours(object):
    """Window to allow user to choose colours for competency statuses. The colours
       are stored in the status_dict dictionary in the supplied database object."""
    def __init__(self, ad: AppData, wnd_colours: ctk.CTkToplevel) -> None:
        logger.info("Competency Status Colour Chooser window")

        self.wnd_colours = wnd_colours
        self.ad = ad

        # Add title top window
        wnd_colours.title("Competency Status Colour Chooser")

        self.frm_attribute = ctk.CTkFrame(wnd_colours)
        self.frm_attribute.pack(fill='both', expand=True)

        row = 0
        self.lbl_default_header = ctk.CTkLabel(self.frm_attribute, text="Default")
        self.lbl_default_header.grid(row=row, column=1, pady=6, padx=10)

        self.lbl_current_header = ctk.CTkLabel(self.frm_attribute, text="Current")
        self.lbl_current_header.grid(row=row, column=2, pady=6, padx=10)

        self.lbl_description = []
        self.btn_default = []
        self.btn_current = []
        self.btn_status_change = []
        for status in ad.status_dict:
            row += 1
            self.lbl_description.append(ctk.CTkLabel(self.frm_attribute, text=ad.status_dict[status]['description']))
            self.lbl_description[status].grid(row=row, column=0, pady=6, padx=10, sticky='e')

            self.btn_default.append(
                ctk.CTkButton(self.frm_attribute,
                              text=colour_to_numbers(ad.status_dict[status]['default']),
                              text_color='black',
                              border_color='black',
                              border_width=2,
                              hover=False,
                              fg_color=ad.status_dict[status]['default']))
            self.btn_default[status].grid(row=row, column=1, pady=6, padx=10)

            self.btn_current.append(
                ctk.CTkButton(self.frm_attribute,
                              text=colour_to_numbers(ad.status_dict[status]['colour']),
                              text_color='black',
                              border_color='black',
                              border_width=2,
                              hover=False,
                              fg_color=ad.status_dict[status]['colour']))
            self.btn_current[status].grid(row=row, column=2, pady=6, padx=10)

            self.btn_status_change.append(ctk.CTkButton(self.frm_attribute, text="Change", width=30))
            if status == 0:
                self.btn_status_change[status].configure(command=lambda: self.colour_chooser(0))
            elif status == 1:
                self.btn_status_change[status].configure(command=lambda: self.colour_chooser(1))
            elif status == 2:
                self.btn_status_change[status].configure(command=lambda: self.colour_chooser(2))
            elif status == 3:
                self.btn_status_change[status].configure(command=lambda: self.colour_chooser(3))
            elif status == 4:
                self.btn_status_change[status].configure(command=lambda: self.colour_chooser(4))
            elif status == 5:
                self.btn_status_change[status].configure(command=lambda: self.colour_chooser(5))
            elif status == 6:
                self.btn_status_change[status].configure(command=lambda: self.colour_chooser(6))

            self.btn_status_change[status].grid(row=row, column=3, pady=6, padx=10, sticky='w')

        row += 1
        self.btn_restore = ctk.CTkButton(self.frm_attribute, text="Restore Defaults", command=self.reset_defaults)
        self.btn_restore.grid(row=row, column=0, pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(self.frm_attribute, text="Exit", command=wnd_colours.destroy)
        self.btn_exit.grid(row=row, column=1, pady=6, padx=10)

    def colour_chooser(self, status: int) -> None:
        """Invoke tkinter colour chooser for specified competency status."""
        # noinspection PyArgumentList
        colour = colorchooser.askcolor(
            master=self.wnd_colours,
            initialcolor=self.ad.status_dict[status]['colour'],
            title=f"{self.ad.status_dict[status]['description']} colour")
        logger.info(f"User chose {colour[1]} for {self.ad.status_dict[status]['description']}")
        if colour[1]:
            self.btn_current[status].configure(fg_color=colour[1], text=colour_to_numbers(str(colour[1])))
            self.ad.status_dict[status]['colour'] = colour[1]

    def reset_defaults(self) -> None:
        """Restore competency status colours to their default values."""
        for status in self.ad.status_dict:
            self.ad.status_dict[status]['colour'] = self.ad.status_dict[status]['default']
            self.btn_current[status].configure(fg_color=self.ad.status_dict[status]['default'],
                                               text=colour_to_numbers(self.ad.status_dict[status]['colour']))


def colour_to_numbers(colour: str) -> str:
    """For a string containing a hexadecimal colour return a string containing
       three decimals separated with spaces."""
    try:
        return (str(int(colour[1:3], 16))
                + ' ' + str(int(colour[3:5], 16))
                + ' ' + str(int(colour[5:7], 16)))
    except ValueError:
        return ""
