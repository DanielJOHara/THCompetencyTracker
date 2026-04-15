"""This module contains the GUI routines to manage the Competency Service table."""
import logging
from typing import Any

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import tkinter as tk

from source.appdata import AppData
from source.competency_display import staff_competency_lists
from source.competency_service_logic import CompetencyServiceLogic
from source.tool_tip import ToolTip, competency_tip_text, role_tip_text

logger = logging.getLogger(__name__)


class CompetencyServiceGrid(object):
    """Generate grid of checkboxes to associate competencies with service areas."""
    def __init__(self, ad: AppData, wnd_cs_grid: ctk.CTkToplevel) -> None:
        logger.info(f"Creating Competency Service Grid window")

        self.wnd_cs_grid = wnd_cs_grid
        self.ad = ad
        self.csl = CompetencyServiceLogic(ad)

        # Set canvas sizes for grid, this will set starting size for scrollable portion of window
        ht_se = 700
        wd_se = 800

        # Add title top window
        wnd_cs_grid.title(f"Competency Service Grid")

        # Define frame to hold grid
        self.frm_rc_grid = ctk.CTkFrame(wnd_cs_grid)
        self.frm_rc_grid.pack(fill='both', expand=True)

        # Define frames to split grid frame into
        #  nw - static top left
        #  ne - header scrollable left and right
        #  sw - row labels scrollable up and down
        #  btn - button frame at bottom of window
        self.frm_nw = ctk.CTkFrame(self.frm_rc_grid)
        self.frm_ne = ctk.CTkFrame(self.frm_rc_grid)
        self.frm_sw = ctk.CTkFrame(self.frm_rc_grid)
        self.frm_se = ctk.CTkFrame(self.frm_rc_grid)

        self.frm_nw.grid(row=0, column=0, sticky='nsew')
        self.frm_ne.grid(row=0, column=1, sticky='nsew')
        self.frm_sw.grid(row=1, column=0, sticky='nsew')
        self.frm_se.grid(row=1, column=1, sticky='nsew')

        # Define scroll bars
        self.vsb = ctk.CTkScrollbar(self.frm_rc_grid, orientation='vertical', command=self.scroll_vertical)
        self.hsb = ctk.CTkScrollbar(self.frm_rc_grid, orientation='horizontal', command=self.scroll_horizontal)

        self.vsb.grid(row=0, column=2, rowspan=2, sticky='ns')
        self.hsb.grid(row=2, column=0, columnspan=2, sticky='ew')

        # Make grid resizeable
        self.frm_rc_grid.grid_rowconfigure(1, weight=1)
        self.frm_rc_grid.grid_columnconfigure(1, weight=1)

        # Canvas with internal frame for three scrollable frames
        self.cnv_ne = tk.Canvas(self.frm_ne, width=wd_se, height=0)
        self.cnv_sw = tk.Canvas(self.frm_sw, width=0, height=ht_se)
        self.cnv_se = tk.Canvas(self.frm_se, width=wd_se, height=ht_se)

        self.frm_cnv_ne = ctk.CTkFrame(self.cnv_ne)
        self.frm_cnv_sw = ctk.CTkFrame(self.cnv_sw)
        self.frm_cnv_se = ctk.CTkFrame(self.cnv_se)

        self.cnv_ne.config(yscrollcommand=self.vsb.set, highlightthickness=0)
        self.cnv_sw.config(xscrollcommand=self.hsb.set, highlightthickness=0)
        self.cnv_se.config(xscrollcommand=self.hsb.set, yscrollcommand=self.vsb.set, highlightthickness=0)

        self.cnv_ne.pack(fill='both', side='left', expand=True)
        self.cnv_sw.pack(fill='both', side='left', expand=True)
        self.cnv_se.pack(fill='both', side='left', expand=True)

        self.cnv_ne.create_window(0, 0, window=self.frm_cnv_ne, anchor='nw')
        self.cnv_sw.create_window(0, 0, window=self.frm_cnv_sw, anchor='nw')
        self.cnv_se.create_window(0, 0, window=self.frm_cnv_se, anchor='nw')

        # Bind on window configure to set scroll regions
        self.wnd_cs_grid.bind('<Configure>', self.handle_configure)

        # Bind mouse wheel for scrolling
        self.cnv_se.bind_all('<MouseWheel>', lambda e: self.handle_mousewheel(e.delta))
        self.cnv_se.bind_all('<Shift-MouseWheel>', lambda e: self.handle_mousewheel_shift(e.delta))
        self.cnv_se.bind_all('<Button-4>', lambda e: self.handle_mousewheel(120))
        self.cnv_se.bind_all('<Button-5>', lambda e: self.handle_mousewheel(-120))
        self.cnv_se.bind_all('<Shift-Button-4>', lambda e: self.handle_mousewheel_shift(120))
        self.cnv_se.bind_all('<Shift-Button-5>', lambda e: self.handle_mousewheel_shift(-120))

        # Populate nw frame - row label
        ht = 30
        wd_c = 250
        self.lbl_competency_name = ctk.CTkLabel(self.frm_nw,
                                                text="Competency Name",
                                                corner_radius=6,
                                                width=wd_c,
                                                height=ht,
                                                anchor='w',
                                                fg_color='#00B0F0')
        self.lbl_competency_name.grid(row=0, column=0, padx=1, pady=1)

        # Write competency rows labels
        self.lbl_row = []
        for db_c in range(self.ad.md.len('Competency')):
            self.lbl_row.append(ctk.CTkLabel(self.frm_cnv_sw,
                                             text=ad.md.get('Competency', 'Competency Name', db_c),
                                             corner_radius=6,
                                             width=wd_c,
                                             height=ht,
                                             anchor='w',
                                             fg_color='#00B0F0'))
            self.lbl_row[db_c].grid(row=db_c, column=0, padx=1, pady=1)

        # Write service colum headers
        wd_r = 60
        self.lbl_column = []
        for db_s in range(self.ad.md.len('Service')):
            service_code = ad.md.get('Service', 'Service Code', db_s)
            self.lbl_column.append(ctk.CTkLabel(self.frm_cnv_ne,
                                                text=service_code,
                                                corner_radius=6,
                                                width=wd_r,
                                                height=ht,
                                                fg_color='#00B0F0'))
            if service_code != 'LEFT':
                self.lbl_column[db_s].grid(row=0, column=db_s, padx=1, pady=1)
                ToolTip(self.lbl_column[db_s], ad.md.get('Service', 'Service Name', db_s))

        # Create grid of check boxes for role competencies
        self.chc_cs = []
        for db_c in range(self.ad.md.len('Competency')):
            competency_name = self.ad.md.get('Competency', 'Competency Name', db_c)
            self.chc_cs.append([])
            for db_s in range(self.ad.md.len('Service')):
                service_code = self.ad.md.get('Service', 'Service Code', db_s)
                self.chc_cs[db_c].append(ctk.CTkCheckBox(self.frm_cnv_se,
                                                         text='',
                                                         width=20,
                                                         height=ht))
                if service_code != 'LEFT':
                    self.chc_cs[db_c][db_s].grid(row=db_c, column=db_s, padx=15, pady=1, sticky='nsew')
                    db_cs = self.ad.md.find_two('Competency Service',
                                                competency_name, 'Competency Name',
                                                service_code, 'Service Code')
                    if db_cs > -1:
                        self.chc_cs[db_c][db_s].select()

        # Create button frame
        self.frm_btn = ctk.CTkFrame(wnd_cs_grid)
        self.frm_btn.pack(fill='x', expand=False)

        self.btn_update = ctk.CTkButton(self.frm_btn, text="Save", command=self.handle_save_click)
        self.btn_update.grid(row=0, column=0, pady=6, padx=10)

        self.btn_add = ctk.CTkButton(self.frm_btn, text="Reset", command=self.handle_reset_click)
        self.btn_add.grid(row=0, column=1, pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(self.frm_btn, text="Exit", command=self.wnd_cs_grid.destroy)
        self.btn_exit.grid(row=0, column=3, pady=6, padx=10)

    def scroll_horizontal(self, *args):
        """Scroll horizontally."""
        self.cnv_se.xview(*args)
        self.cnv_ne.xview(*args)

    def scroll_vertical(self, *args):
        """Scroll vertically."""
        self.cnv_se.yview(*args)
        self.cnv_sw.yview(*args)

    def handle_configure(self, event: Any):
        """On window configure set frame scroll regions."""
        logger.debug(f"Called with event {event}")
        self.cnv_ne.config(scrollregion=self.frm_cnv_ne.bbox())
        self.cnv_sw.config(scrollregion=self.frm_cnv_sw.bbox())
        self.cnv_se.config(scrollregion=self.frm_cnv_se.bbox())

    def handle_mousewheel(self, event: int):
        """Scroll vertically for mouse wheel."""
        self.cnv_se.yview_scroll(int(-1 * (event / 120)), 'units')
        self.cnv_sw.yview_scroll(int(-1 * (event / 120)), 'units')

    def handle_mousewheel_shift(self, event: int):
        """Scroll horizontally for mouse wheel."""
        self.cnv_ne.xview_scroll(int(-1 * (event / 120)), 'units')
        self.cnv_se.xview_scroll(int(-1 * (event / 120)), 'units')

    def handle_save_click(self):
        """Read all values in checkbox grid and check them against the
           Competency Service table and add and delete records as required."""

        number_changes = self.csl.save_all_competency_service(self.chc_cs)
        CTkMessagebox(title="Information", message=f"{number_changes} changes saved", icon='info')

    def handle_reset_click(self):
        """Read all values in checkbox grid and check them against the
           Role Competency table and set checkboxes to the table values."""

        self.csl.reset_competency_service(self.chc_cs)


class CompetencyServiceUpdate:
    """Generate a window to update the Service Codes foe an individual Competency."""
    def __init__(self,
                 ad: AppData,
                 wnd_cs_update: ctk.CTkToplevel,
                 competency_name: str) -> None:
        logger.info("Creating Competency Service data update window")

        self.ad = ad
        self.wnd_cs_update = wnd_cs_update
        self.competency_name = competency_name
        self.csl = CompetencyServiceLogic(ad)

        # Add title top window
        wnd_cs_update.title("Competency Service Data Update")

        self.frm_attribute = ctk.CTkFrame(wnd_cs_update)
        self.frm_attribute.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_competency_name = ctk.CTkLabel(self.frm_attribute, text="Competency Name")
        self.lbl_competency_name.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_competency_name = ctk.CTkEntry(self.frm_attribute, width=250)
        self.cmb_competency_name.insert(0, self.competency_name)
        self.cmb_competency_name.configure(state='disabled')
        self.cmb_competency_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_service_code = ctk.CTkLabel(self.frm_attribute, text="Service Codes")
        self.lbl_service_code.grid(row=row, column=0, pady=6, padx=10, sticky='w')

        self.cmb_service_code_list = []
        self.chc_service_code_list = []
        row -= 1
        for db_s in range(self.ad.md.len('Service')):
            service_code = self.ad.md.get('Service', 'Service Code', db_s)
            self.chc_service_code_list.append(ctk.CTkCheckBox(self.frm_attribute, text=service_code, width=40))
            if service_code != 'LEFT':
                row += 1
                self.chc_service_code_list[db_s].grid(row=row, column=1, pady=6, padx=10, sticky='w')
                if self.ad.md.find_two('Competency Service',
                                       competency_name, 'Competency Name',
                                       service_code, 'Service Code') > -1:
                    self.chc_service_code_list[db_s].select()

        self.btn_update = ctk.CTkButton(self.wnd_cs_update, text="Save", command=self.handle_save_click)
        self.btn_update.pack(pady=6, padx=10)

        self.btn_delete = ctk.CTkButton(self.wnd_cs_update, text="Delete", command=self.handle_delete_click)
        self.btn_delete.pack(pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(self.wnd_cs_update, text="Exit", command=self.wnd_cs_update.destroy)
        self.btn_exit.pack(pady=6, padx=10)

    def handle_save_click(self):
        """Apply the services selected for the competency by he user."""
        number_changes = self.csl.save_competency_service(self.competency_name, self.chc_service_code_list)
        CTkMessagebox(title="Information", message=f"{number_changes} changes saved", icon='info')

    def handle_delete_click(self):
        for chc_service_code in self.chc_service_code_list:
            chc_service_code.deselect()
        number_changes = self.csl.save_competency_service(self.competency_name, self.chc_service_code_list)
        CTkMessagebox(title="Information", message=f"{number_changes} records deleted", icon='info')
