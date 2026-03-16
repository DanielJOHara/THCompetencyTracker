"""This module contains the GUI routines to manage the Staff Role table."""
import logging
from typing import Any

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from source.appdata import AppData
from source.staff_role_logic import StaffRoleLogic
from source.window import input_warning, widget_list_values

logger = logging.getLogger(__name__)


class StaffRoleUpdate(object):
    """Window to allow user to update Staff Role data."""
    def __init__(self,
                 ad: AppData,
                 wnd_staff_role: ctk.CTkToplevel,
                 staff_name: str = None) -> None:
        logger.info("Creating Staff Role data update window")

        self.wnd_staff_role = wnd_staff_role
        self.ad = ad
        self.srl = StaffRoleLogic(ad)
        self.staff_name = staff_name

        # Add title top window
        wnd_staff_role.title("Staff Role Data Update")

        self.frm_attribute = ctk.CTkFrame(wnd_staff_role)
        self.frm_attribute.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_staff_name = ctk.CTkLabel(self.frm_attribute, text="Staff Name")
        self.lbl_staff_name.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_staff_name = ctk.CTkComboBox(self.frm_attribute, state='readonly',
                                              values=ad.md.get_list('Staff', 'Staff Name'), command=self.refresh_staff)
        self.cmb_staff_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        col = 0
        self.lbl_service_code = ctk.CTkLabel(self.frm_attribute, text="Service Code")
        self.lbl_service_code.grid(row=row, column=col, pady=6, padx=10, sticky='w')

        col += 1
        self.lbl_role_code = ctk.CTkLabel(self.frm_attribute, text="Role Code")
        self.lbl_role_code.grid(row=row, column=col, pady=6, padx=10, sticky='w')

        col += 1
        self.lbl_bank = ctk.CTkLabel(self.frm_attribute, text="Bank", width=40)
        self.lbl_bank.grid(row=row, column=col, pady=6, padx=10, sticky='w')

        col += 1
        self.lbl_bank = ctk.CTkLabel(self.frm_attribute, text="Nightshift", width=40)
        self.lbl_bank.grid(row=row, column=col, pady=6, padx=10, sticky='w')

        self.ent_service_code = []
        self.chc_bank = []
        self.chc_nightshift = []
        self.cmb_role_code = []
        for db_sc, service_code in enumerate(ad.md.get_list('Service', 'Service Code')):
            row += 1
            col = 0
            self.ent_service_code.append(ctk.CTkEntry(self.frm_attribute))
            self.ent_service_code[db_sc].grid(row=row, column=col, pady=6, padx=10, sticky='w')
            self.ent_service_code[db_sc].insert(0, service_code)
            self.ent_service_code[db_sc].configure(state='disabled')

            col += 1
            self.cmb_role_code.append(ctk.CTkComboBox(self.frm_attribute, state='readonly',
                                                      values=[''] + ad.md.get_list('Role', 'Role Code')))
            self.cmb_role_code[db_sc].grid(row=row, column=col, pady=6, padx=10, sticky='w')

            col += 1
            self.chc_bank.append(ctk.CTkCheckBox(self.frm_attribute, text="", width=40))
            self.chc_bank[db_sc].grid(row=row, column=col, pady=6, padx=10)

            col += 1
            self.chc_nightshift.append(ctk.CTkCheckBox(self.frm_attribute, text="", width=40))
            self.chc_nightshift[db_sc].grid(row=row, column=col, pady=6, padx=10)

        # Check that we are not in single staff member mode
        if not self.staff_name:
            # Create lookup frame for name filter
            self.frm_lookup = ctk.CTkFrame(wnd_staff_role)
            self.frm_lookup.pack(fill='both', side='left', expand=True)

            row = 0
            self.lbl_name_filter = ctk.CTkLabel(self.frm_lookup, text="Name Filter")
            self.lbl_name_filter.grid(row=row, column=0, pady=6, padx=10, sticky='e')
            self.ent_name_filter = ctk.CTkEntry(self.frm_lookup)
            self.ent_name_filter.grid(row=row, column=1, pady=6, padx=10, sticky='w')
            self.ent_name_filter.bind("<Return>", command=self.filter_names)
            self.ent_name_filter.bind("<Leave>", command=self.filter_names)

            # Multiple record action buttons
            self.btn_next = ctk.CTkButton(wnd_staff_role, text="Next", command=self.handle_next_click)
            self.btn_next.pack(pady=6, padx=10)

            self.btn_previous = ctk.CTkButton(wnd_staff_role, text="Previous", command=self.handle_previous_click)
            self.btn_previous.pack(pady=6, padx=10)

        # Single and multiple staff member update buttons
        self.btn_update = ctk.CTkButton(wnd_staff_role, text="Save", command=self.handle_save_click)
        self.btn_update.pack(pady=6, padx=10)

        self.btn_delete = ctk.CTkButton(wnd_staff_role, text="Delete", command=self.handle_delete_click)
        self.btn_delete.pack(pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(wnd_staff_role, text="Exit", command=self.wnd_staff_role.destroy)
        self.btn_exit.pack(pady=6, padx=10)

        # Set Staff table row to the length of table
        self.db_s = ad.md.len('Staff')

        if self.staff_name:
            self.cmb_staff_name.set(self.staff_name)
            self.cmb_staff_name.configure(state='disabled')
            self.refresh_staff()

    def refresh_staff(self, event: Any = None):
        """When a Staff Name is selected load its Staff Role records."""
        logger.debug(f"Called with event {event}")
        staff_name = self.cmb_staff_name.get()
        if staff_name:
            db_s = self.ad.md.find_one('Staff', staff_name, 'Staff Name')
            if db_s > -1:
                self.db_s = db_s
                for db_sc, service_code in enumerate(self.ad.md.get_list('Service', 'Service Code')):
                    self.cmb_role_code[db_sc].set('')
                    self.chc_bank[db_sc].deselect()
                    self.chc_nightshift[db_sc].deselect()
                    db_sr = self.ad.md.find_two('Staff Role', service_code, 'Service Code', staff_name, 'Staff Name')
                    if db_sr > -1:
                        self.cmb_role_code[db_sc].set(self.ad.md.get('Staff Role', 'Role Code', db_sr))
                        if self.ad.md.get('Staff Role', 'Bank', db_sr):
                            self.chc_bank[db_sc].select()
                        if self.ad.md.get('Staff Role', 'Nightshift', db_sr):
                            self.chc_nightshift[db_sc].select()

    def handle_next_click(self):
        """Move on to next Staff Role record."""
        if self.db_s >= self.ad.md.len('Staff') - 1:
            self.db_s = 0
        else:
            self.db_s += 1
        self.cmb_staff_name.set(self.ad.md.get('Staff', 'Staff Name', self.db_s))
        self.refresh_staff()

    def handle_previous_click(self):
        """Move on to previous Staff Role record."""
        if self.db_s <= 0:
            self.db_s = self.ad.md.len('Staff') - 1
        else:
            self.db_s -= 1
        self.cmb_staff_name.set(self.ad.md.get('Staff', 'Staff Name', self.db_s))
        self.refresh_staff()

    def handle_delete_click(self):
        """Delete role records for staff member, don't need check use in other tables."""
        staff_name = self.cmb_staff_name.get()
        self.srl.delete_staff_roles(staff_name)
        self.refresh_staff()

    def handle_save_click(self):
        """Update role records for current staff member."""
        staff_name = self.cmb_staff_name.get()
        input_valid, number_changes, message = self.srl.save_staff_roles(staff_name,
                                                                         widget_list_values(self.cmb_role_code),
                                                                         widget_list_values(self.chc_bank),
                                                                         widget_list_values(self.chc_nightshift))
        if not input_valid:
            input_warning(self.wnd_staff_role, message)
            return

        # If we are entering data for a single staff member close on save
        if self.staff_name:
            self.wnd_staff_role.destroy()
            return

        CTkMessagebox(title="Information", message=message, icon='info')

        if number_changes > 0:
            self.refresh_staff()

    def filter_names(self, event: Any = None) -> None:
        """Filter the names in the Staff Name drop down to those that match
           the filter entered by the user."""
        logger.debug(f"Called with event {event}")
        name_filter = self.ent_name_filter.get()
        filtered_names = self.srl.filter_staff_names(name_filter)
        self.cmb_staff_name.configure(values=filtered_names)

        # If the filter returns a single name set it in the staff name field
        if len(filtered_names) == 1:
            self.cmb_staff_name.set(filtered_names[0])
            self.refresh_staff()
        # if the current staff name is not in the list blank all the fields
        elif self.cmb_staff_name.get() not in filtered_names:
            self.cmb_staff_name.set('')
            for s in range(self.ad.md.len('Service')):
                self.cmb_role_code[s].set('')
                self.chc_bank[s].deselect()
                self.chc_nightshift[s].deselect()
