"""This module generates grid of checkboxes to set the roles required for competencies."""
import logging

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import tkinter as tk

from source.appdata import AppData
from source.competency_display import staff_competency_lists
from source.tool_tip import ToolTip, competency_tip_text, role_tip_text

logger = logging.getLogger(__name__)


class RoleCompetencyGrid(object):
    """Generate grid of checkboxes to set the roles required for competencies
       for a service area staff type combination."""
    def __init__(self, ad: AppData, wnd_rc_grid: ctk.CTkToplevel, service_code: str, staff_type: str) -> None:
        logger.info(f"Creating Role Competency Grid window for {service_code} {staff_type}")

        self.wnd_rc_grid = wnd_rc_grid
        self.ad = ad
        self.service_code = service_code
        self.staff_type = staff_type

        # Set canvas sizes for grid, this will set starting size for scrollable portion of window
        ht_se = 700
        wd_se = 800

        # Add title top window
        wnd_rc_grid.title(f"Role Competency Grid for {service_code} {staff_type}")

        # Define frame to hold grid
        self.frm_rc_grid = ctk.CTkFrame(wnd_rc_grid)
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
        self.wnd_rc_grid.bind('<Configure>', self.handle_configure)

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

        # Create a lists of Competencies for the Staff Type
        # The staff list is not used here
        self.db_c_list = []
        for db_c in range(ad.md.len('Competency')):
            if ad.md.get('Competency', 'Scope', db_c) in [staff_type, 'BOTH']:
                self.db_c_list.append(db_c)

        # Write competency rows labels
        self.lbl_row = []
        db_s_list, db_c_list = staff_competency_lists(ad, service_code, staff_type)
        for c, db_c in enumerate(self.db_c_list):
            self.lbl_row.append(ctk.CTkLabel(self.frm_cnv_sw,
                                             text=ad.md.get('Competency', 'Competency Name', db_c),
                                             corner_radius=6,
                                             width=wd_c,
                                             height=ht,
                                             anchor='w',
                                             fg_color='#00B0F0'))
            self.lbl_row[c].grid(row=c, column=0, padx=1, pady=1)

            tip_text = competency_tip_text(ad, db_c, db_s_list, service_code, staff_type)
            ToolTip(self.lbl_row[c], tip_text)

        # Create list of Roles relevant to the staff type
        self.db_r_list = []
        for db_r in range(self.ad.md.len('Role')):
            rn = self.ad.md.get('Role', 'RN', db_r)
            if rn and staff_type == 'RN' or not rn and staff_type != 'RN':
                self.db_r_list.append(db_r)

        # Write role colum headers
        wd_r = 60
        self.lbl_column = []
        for r, db_r in enumerate(self.db_r_list):
            self.lbl_column.append(ctk.CTkLabel(self.frm_cnv_ne,
                                                text=ad.md.get('Role', 'Role Code', db_r),
                                                corner_radius=6,
                                                width=wd_r,
                                                height=ht,
                                                fg_color='#00B0F0'))
            self.lbl_column[r].grid(row=0, column=r, padx=1, pady=1)

            tip_text = role_tip_text(ad, db_r, service_code)
            ToolTip(self.lbl_column[r], tip_text)

        # Create grid of check boxes for role competencies
        self.chc_rc = []
        for c, db_c in enumerate(self.db_c_list):
            competency_name = self.ad.md.get('Competency', 'Competency Name', db_c)
            self.chc_rc.append([])
            for r, db_r in enumerate(self.db_r_list):
                role_code = self.ad.md.get('Role', 'Role Code', db_r)
                self.chc_rc[c].append(ctk.CTkCheckBox(self.frm_cnv_se,
                                                      text='',
                                                      width=20,
                                                      height=ht))
                self.chc_rc[c][r].grid(row=c, column=r, padx=15, pady=1, sticky='nsew')
                db_rc = self.ad.md.find_three('Role Competency',
                                              service_code, 'Service Code',
                                              role_code, 'Role Code',
                                              competency_name, 'Competency Name')
                if db_rc > -1:
                    self.chc_rc[c][r].select()

        # Create button frame
        self.frm_btn = ctk.CTkFrame(wnd_rc_grid)
        self.frm_btn.pack(fill='x', expand=False)

        self.btn_update = ctk.CTkButton(self.frm_btn, text="Save", command=self.handle_save_click)
        self.btn_update.grid(row=0, column=0, pady=6, padx=10)

        self.btn_add = ctk.CTkButton(self.frm_btn, text="Reset", command=self.handle_reset_click)
        self.btn_add.grid(row=0, column=1, pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(self.frm_btn, text="Exit", command=self.wnd_rc_grid.destroy)
        self.btn_exit.grid(row=0, column=3, pady=6, padx=10)

    def scroll_horizontal(self, *args):
        """Scroll horizontally."""
        self.cnv_se.xview(*args)
        self.cnv_ne.xview(*args)

    def scroll_vertical(self, *args):
        """Scroll vertically."""
        self.cnv_se.yview(*args)
        self.cnv_sw.yview(*args)

    # noinspection PyUnusedLocal
    def handle_configure(self, event):
        """On window configure set frame scroll regions."""
        self.cnv_ne.config(scrollregion=self.frm_cnv_ne.bbox())
        self.cnv_sw.config(scrollregion=self.frm_cnv_sw.bbox())
        self.cnv_se.config(scrollregion=self.frm_cnv_se.bbox())

    def handle_mousewheel(self, event):
        """Scroll vertically for mouse wheel."""
        self.cnv_se.yview_scroll(int(-1 * (event / 120)), 'units')
        self.cnv_sw.yview_scroll(int(-1 * (event / 120)), 'units')

    def handle_mousewheel_shift(self, event):
        """Scroll horizontally for mouse wheel."""
        self.cnv_ne.xview_scroll(int(-1 * (event / 120)), 'units')
        self.cnv_se.xview_scroll(int(-1 * (event / 120)), 'units')

    def handle_save_click(self):
        """Read all values in checkbox grid and check them against the
           Role Competency table and add and delete records as required."""

        number_changes = 0
        for c, db_c in enumerate(self.db_c_list):
            competency_name = self.ad.md.get('Competency', 'Competency Name', db_c)
            for r, db_r in enumerate(self.db_r_list):
                role_code = self.ad.md.get('Role', 'Role Code', db_r)
                chc_status = self.chc_rc[c][r].get()
                db_rc = self.ad.md.find_three('Role Competency',
                                              self.service_code, 'Service Code',
                                              role_code, 'Role Code',
                                              competency_name, 'Competency Name')

                # If there is a record for Role Competency combination and its checkbox is unchecked then delete it
                if db_rc > -1:
                    if not chc_status:
                        number_changes += 1
                        self.ad.master_updated = True
                        self.ad.md.delete_row('Role Competency', db_rc)

                # If there is no record for Role Competency combination and its checkbox is checked add one
                else:
                    if chc_status:
                        number_changes += 1
                        self.ad.master_updated = True
                        self.ad.md.add_row('Role Competency', {'Service Code': self.service_code,
                                                               'Role Code': role_code,
                                                               'Competency Name': competency_name})

        CTkMessagebox(title="Information", message=f"{number_changes} changes saved", icon='info')

    def handle_reset_click(self):
        """Read all values in checkbox grid and check them against the
           Role Competency table and set checkboxes to the table values."""

        for c, db_c in enumerate(self.db_c_list):
            competency_name = self.ad.md.get('Competency', 'Competency Name', db_c)
            for r, db_r in enumerate(self.db_r_list):
                role_code = self.ad.md.get('Role', 'Role Code', db_r)
                chc_status = self.chc_rc[c][r].get()
                db_rc = self.ad.md.find_three('Role Competency',
                                              self.service_code, 'Service Code',
                                              role_code, 'Role Code',
                                              competency_name, 'Competency Name')

                # If there is a record for Role Competency combination and its checkbox is not checked then check it
                if db_rc > -1:
                    if not chc_status:
                        self.chc_rc[c][r].select()

                # If there is no record for Role Competency combination and its checkbox is checked then uncheck it
                else:
                    if chc_status:
                        self.chc_rc[c][r].deselect()
