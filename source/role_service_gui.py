"""This module contains the GUI routines to manage the Role Service table."""
import logging
from typing import Any

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import tkinter as tk

from source.appdata import AppData
from source.role_service_logic import RoleServiceLogic
from source.tool_tip import ToolTip

logger = logging.getLogger(__name__)


class RoleServiceGrid(object):
    """Generate grid of checkboxes to associate roles with service areas."""
    def __init__(self, ad: AppData, wnd_cs_grid: ctk.CTkToplevel) -> None:
        logger.info(f"Creating Role Service Grid window")

        self.wnd_cs_grid = wnd_cs_grid
        self.ad = ad
        self.rsl = RoleServiceLogic(ad)

        # Set canvas sizes for grid, this will set starting size for scrollable portion of window
        ht_se = 700
        wd_se = 800

        # Add title top window
        wnd_cs_grid.title(f"Role Service Grid")

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
        wd_rn = 250
        wd_rc = 90
        self.lbl_role_name = ctk.CTkLabel(self.frm_nw,
                                          text="Role Name",
                                          corner_radius=6,
                                          width=wd_rn,
                                          height=ht,
                                          anchor='w',
                                          fg_color='#00B0F0')
        self.lbl_role_name.grid(row=0, column=0, padx=1, pady=1)

        self.lbl_role_code = ctk.CTkLabel(self.frm_nw,
                                          text="Role Code",
                                          corner_radius=6,
                                          width=wd_rc,
                                          height=ht,
                                          anchor='w',
                                          fg_color='#00B0F0')
        self.lbl_role_code.grid(row=0, column=2, padx=1, pady=1)

        # Write Role rows labels
        self.lbl_row = []
        for db_r in range(self.ad.md.len('Role')):
            self.lbl_row.append([])
            
            self.lbl_row[db_r].append(ctk.CTkLabel(self.frm_cnv_sw,
                                                   text=ad.md.get('Role', 'Role Name', db_r),
                                                   corner_radius=6,
                                                   width=wd_rn,
                                                   height=ht,
                                                   anchor='w',
                                                   fg_color='#00B0F0'))
            self.lbl_row[db_r][0].grid(row=db_r, column=0, padx=1, pady=1)

            self.lbl_row[db_r].append(ctk.CTkLabel(self.frm_cnv_sw,
                                                   text=ad.md.get('Role', 'Role Code', db_r),
                                                   corner_radius=6,
                                                   width=wd_rc,
                                                   height=ht,
                                                   anchor='w',
                                                   fg_color='#00B0F0'))
            self.lbl_row[db_r][1].grid(row=db_r, column=1, padx=1, pady=1)

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
        for db_r in range(self.ad.md.len('Role')):
            role_code = self.ad.md.get('Role', 'Role Code', db_r)
            self.chc_cs.append([])
            for db_s in range(self.ad.md.len('Service')):
                service_code = self.ad.md.get('Service', 'Service Code', db_s)
                self.chc_cs[db_r].append(ctk.CTkCheckBox(self.frm_cnv_se,
                                                         text='',
                                                         width=20,
                                                         height=ht))
                if service_code != 'LEFT':
                    self.chc_cs[db_r][db_s].grid(row=db_r, column=db_s, padx=15, pady=1, sticky='nsew')
                    db_rs = self.ad.md.find_two('Role Service',
                                                role_code, 'Role Code',
                                                service_code, 'Service Code')
                    if db_rs > -1:
                        self.chc_cs[db_r][db_s].select()

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
           Role Service table and add and delete records as required."""

        number_changes = self.rsl.save_all_role_service(self.chc_cs)
        CTkMessagebox(title="Information", message=f"{number_changes} changes saved", icon='info')

    def handle_reset_click(self):
        """Read all values in checkbox grid and check them against the
           Role Service table and set checkboxes to the table values."""

        self.rsl.reset_role_service(self.chc_cs)


class RoleServiceUpdate:
    """Generate a window to update the Role Codes for an individual Role."""
    def __init__(self,
                 ad: AppData,
                 wnd_rs_update: ctk.CTkToplevel,
                 role_code: str) -> None:
        logger.info("Creating Role Service data update window")

        self.ad = ad
        self.wnd_rs_update = wnd_rs_update
        self.role_code = role_code
        self.rsl = RoleServiceLogic(ad)

        # Add title top window
        wnd_rs_update.title("Role Service Data Update")

        self.frm_attribute = ctk.CTkFrame(wnd_rs_update)
        self.frm_attribute.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_role_code = ctk.CTkLabel(self.frm_attribute, text="Role Code")
        self.lbl_role_code.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_role_code = ctk.CTkEntry(self.frm_attribute, width=90)
        self.cmb_role_code.insert(0, self.role_code)
        self.cmb_role_code.configure(state='disabled')
        self.cmb_role_code.grid(row=row, column=1, pady=6, padx=10, sticky='w')

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
                if self.ad.md.find_two('Role Service',
                                       role_code, 'Role Code',
                                       service_code, 'Service Code') > -1:
                    self.chc_service_code_list[db_s].select()

        self.btn_update = ctk.CTkButton(self.wnd_rs_update, text="Save", command=self.handle_save_click)
        self.btn_update.pack(pady=6, padx=10)

        self.btn_delete = ctk.CTkButton(self.wnd_rs_update, text="Delete", command=self.handle_delete_click)
        self.btn_delete.pack(pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(self.wnd_rs_update, text="Exit", command=self.wnd_rs_update.destroy)
        self.btn_exit.pack(pady=6, padx=10)

    def handle_save_click(self):
        """Apply the services selected for the role by he user."""
        number_changes = self.rsl.save_role_service(self.role_code, self.chc_service_code_list)
        CTkMessagebox(title="Information", message=f"{number_changes} changes saved", icon='info')

    def handle_delete_click(self):
        for chc_service_code in self.chc_service_code_list:
            chc_service_code.deselect()
        number_changes = self.rsl.save_role_service(self.role_code, self.chc_service_code_list)
        CTkMessagebox(title="Information", message=f"{number_changes} records deleted", icon='info')
