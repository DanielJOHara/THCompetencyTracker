"""This module contains the GUI routines to manage the Role table."""
import logging
import re
from typing import Any

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import tkinter as tk

from source.appdata import AppData
from source.role_logic import RoleUpdateLogic
from source.role_service_gui import RoleServiceUpdate
from source.window import child_window, set_disabled_checkbox, set_disabled_entry, input_warning, widget_dict_values

logger = logging.getLogger(__name__)


class RoleUpdate(object):
    """Window to allow user to update Role data using a table."""
    def __init__(self, ad: AppData, wnd_role: ctk.CTkToplevel) -> None:
        """Window to allow user to update Role data in a table."""
        logger.info("Creating Role Table data update window")

        self.wnd_role = wnd_role
        self.ad = ad
        self.rul = RoleUpdateLogic(ad)

        # Add title top window
        wnd_role.title("Role Data Update")

        # Create header frame, pad to align with scrollable frame
        self.frm_h = ctk.CTkFrame(self.wnd_role)
        self.frm_h.pack(padx=6, fill='x', expand=False)

        self.header = ['Display Order', 'Role Code', 'Role Name', 'RN', 'Services']
        self.width = [90, 90, 250, 90, 150]

        # Create list to hold header labels
        self.lbl_header = []

        # Display header row
        for x in range(len(self.header)):
            self.lbl_header.append(ctk.CTkLabel(self.frm_h, text=self.header[x], height=30, width=self.width[x],
                                                corner_radius=6, fg_color='#00B0F0'))
            self.lbl_header[x].grid(row=0, column=x)

        # Create scrollable frame
        self.frm_s = ctk.CTkScrollableFrame(wnd_role)
        self.frm_s.pack(fill='both', expand=True)

        # Create lists to hold column widgets
        self.role_widgets = []

        # Display widgets for all role records
        for db_r in range(ad.md.len('Role')):
            self.add_role_to_display(db_r)

        # Create button frame
        self.frm_btn = ctk.CTkFrame(wnd_role)
        self.frm_btn.pack(fill='x', expand=False)

        self.btn_update = ctk.CTkButton(self.frm_btn, text="Save", command=self.handle_save_click)
        self.btn_update.grid(row=0, column=0, pady=6, padx=10)

        self.btn_add = ctk.CTkButton(self.frm_btn, text="Add", command=self.handle_add_click)
        self.btn_add.grid(row=0, column=1, pady=6, padx=10)

        self.btn_add = ctk.CTkButton(self.frm_btn, text="Delete", command=self.handle_delete_click)
        self.btn_add.grid(row=0, column=2, pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(self.frm_btn, text="Exit", command=wnd_role.destroy)
        self.btn_exit.grid(row=0, column=3, pady=6, padx=10)

    def handle_save_click(self):
        """Read all values in table and update the table object if any values have changed."""
        role_values = widget_dict_values(self.role_widgets)
        input_valid, number_changes, message = self.rul.save_roles(role_values)

        if not input_valid:
            input_warning(self.wnd_role, message)
            return

        CTkMessagebox(title="Information", message=message, icon='info')

        # Sort table and refresh display
        if number_changes > 0:
            self.display_role_table()

    def handle_add_click(self):
        """Prompt user for row to be added."""
        # Invoke function to add row to table
        child_window(RoleAdd, self.ad, self.wnd_role)

        # Refresh table, this will add any extra rows
        self.display_role_table()

    def handle_delete_click(self):
        # Call window to delete roles
        child_window(RoleDelete, self.ad, self.wnd_role)

        # Remove a row from the table for each deleted record
        for i in range(len(self.role_widgets) - self.ad.md.len('Role')):
            # Remove last row of widgets
            self.role_widgets[-1]['Display Order'].destroy()
            self.role_widgets[-1]['Role Code'].destroy()
            self.role_widgets[-1]['Role Name'].destroy()
            self.role_widgets[-1]['RN'].destroy()
            self.role_widgets.pop()

        # Re-display table
        self.display_role_table()

    def display_role_table(self):
        """Display widgets for all role records."""
        for db_r in range(self.ad.md.len('Role')):
            self.add_role_to_display(db_r)

    def add_role_to_display(self, db_r: int):
        """Display a row of widgets for a specified Role table index."""
        if db_r + 1 > len(self.role_widgets):
            self.role_widgets.append({
                'Display Order': ctk.CTkEntry(self.frm_s, width=self.width[0]),
                'Role Code': ctk.CTkEntry(self.frm_s, width=self.width[1]),
                'Role Name': ctk.CTkEntry(self.frm_s, width=self.width[2]),
                'RN': ctk.CTkCheckBox(self.frm_s, width=self.width[3] - 2 * int(self.width[3] / 3), text=""),
                'Service': ctk.CTkLabel(self.frm_s, width=self.width[4], height=24,
                                        text_color='#808080', fg_color='#FFFFFF', anchor='w')
            })
            self.role_widgets[db_r]['Display Order'].grid(row=db_r + 1, column=0, sticky='w')
            self.role_widgets[db_r]['Role Code'].grid(row=db_r + 1, column=1, sticky='w')
            self.role_widgets[db_r]['Role Name'].grid(row=db_r + 1, column=2, sticky='w')
            self.role_widgets[db_r]['RN'].grid(row=db_r + 1, column=3, sticky='nsew', padx=int(self.width[3] / 3))
            self.role_widgets[db_r]['Service'].grid(row=db_r + 1, column=4, sticky='w')
            # Add binding so click on service entry calls routine to update the services
            self.role_widgets[db_r]['Service'].bind('<Button-1>', self.handel_service_click)

        self.role_widgets[db_r]['Display Order'].delete(0, 9999)
        self.role_widgets[db_r]['Display Order'].insert(0, self.ad.md.get('Role', 'Display Order', db_r))

        role_code = self.ad.md.get('Role', 'Role Code', db_r)
        self.role_widgets[db_r]['Role Code'].delete(0, 9999)
        self.role_widgets[db_r]['Role Code'].insert(0, role_code)

        self.role_widgets[db_r]['Role Name'].delete(0, 9999)
        self.role_widgets[db_r]['Role Name'].insert(0, self.ad.md.get('Role', 'Role Name', db_r))

        if self.ad.md.get('Role', 'RN', db_r):
            self.role_widgets[db_r]['RN'].select()
        else:
            self.role_widgets[db_r]['RN'].deselect()

        service_list = ' '
        for db_s in range(self.ad.md.len('Service')):
            service_code = self.ad.md.get('Service', 'Service Code', db_s)
            if self.ad.md.find_two('Role Service',
                                   role_code, 'Role Code',
                                   service_code, 'Service Code') > -1:
                service_list += service_code + ', '
        self.role_widgets[db_r]['Service'].configure(text=service_list[:-2])

    def handel_service_click(self, event: tk.Event):
        logger.debug(f"Click from event widget [{event.widget}]")
        # Extract label number from widget
        label_num_search = re.search(r'ctklabel(\d+)?', str(event.widget))
        if not label_num_search:
            logger.error(f"Failed to extract label number from event widget [{event.widget}]")
            return

        # First label has no number
        if not label_num_search.group(1):
            db_r = 0
        else:
            db_r = int(label_num_search.group(1)) - 1

        role_code = self.ad.md.get('Role', 'Role Code', db_r)
        child_window(RoleServiceUpdate, self.ad, self.wnd_role, role_code)

        service_list = ' '
        for db_s in range(self.ad.md.len('Service')):
            service_code = self.ad.md.get('Service', 'Service Code', db_s)
            if self.ad.md.find_two('Role Service',
                                   role_code, 'Role Code',
                                   service_code, 'Service Code') > -1:
                service_list += service_code + ', '
        self.role_widgets[db_r]['Service'].configure(text=service_list[:-2])


class RoleDelete(object):
    """Window to allow user to delete Role data records."""
    def __init__(self, ad: AppData, wnd_role_del: ctk.CTkToplevel) -> None:
        logger.info(f"Creating Role data delete window")

        self.wnd_role_del = wnd_role_del
        self.ad = ad
        self.rul = RoleUpdateLogic(ad)

        # Add title top window
        wnd_role_del.title("Role Data Delete")

        self.frm_attribute = ctk.CTkFrame(wnd_role_del)
        self.frm_attribute.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_role_code = ctk.CTkLabel(self.frm_attribute, text="Role Code")
        self.lbl_role_code.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_role_code = ctk.CTkComboBox(self.frm_attribute, state='readonly',
                                             values=ad.md.get_list('Role', 'Role Code'), command=self.refresh_role)
        self.cmb_role_code.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_role_name = ctk.CTkLabel(self.frm_attribute, text="Role Name")
        self.lbl_role_name.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_role_name = ctk.CTkEntry(self.frm_attribute, state='disabled')
        self.ent_role_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_display_order = ctk.CTkLabel(self.frm_attribute, text="Display Order")
        self.lbl_display_order.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_display_order = ctk.CTkEntry(self.frm_attribute, state='disabled')
        self.ent_display_order.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.chc_rn = ctk.CTkCheckBox(self.frm_attribute, text="RN", state='disabled')
        self.chc_rn.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        # Action Buttons
        self.btn_delete = ctk.CTkButton(wnd_role_del, text="Delete", command=self.handle_delete_click)
        self.btn_delete.pack(pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(wnd_role_del, text="Exit", command=wnd_role_del.destroy)
        self.btn_exit.pack(pady=6, padx=10)

    def refresh_role(self, event: Any):
        """Display the role record selected."""
        logger.debug(f"Called with event {event}")
        # Identify selected role code
        role_code = self.cmb_role_code.get()
        db_r = self.ad.md.index('Role', 'Role Code', role_code)

        set_disabled_entry(self.ent_role_name, self.ad.md.get('Role', 'Role Name', db_r))
        set_disabled_entry(self.ent_display_order, self.ad.md.get('Role', 'Display Order', db_r))
        set_disabled_checkbox(self.chc_rn, self.ad.md.get('Role', 'RN', db_r))

    def handle_delete_click(self):
        """Delete current record."""
        role_code = self.cmb_role_code.get()
        success, warning, message = self.rul.delete_role(role_code)

        if not success:
            if warning:
                msg = CTkMessagebox(title="Dependent Record Warning", message=message,
                                    icon='warning', option_1='Delete', option_2='Cancel')
                if msg.get() == 'Cancel':
                    self.wnd_role_del.grab_set()
                    return
                self.wnd_role_del.grab_set()
                self.rul.delete_role_with_dependents(role_code)

        # Clear widgets
        self.cmb_role_code.set('')
        self.cmb_role_code.configure(values=self.ad.md.get_list('Role', 'Role Code'))
        set_disabled_entry(self.ent_role_name, '')
        set_disabled_entry(self.ent_display_order, '')
        set_disabled_checkbox(self.chc_rn, 0)


class RoleAdd(object):
    """Window to allow user to add  a single record Role data record."""
    def __init__(self, ad: AppData, wnd_role_add: ctk.CTkToplevel) -> None:
        logger.info(f"Creating Role data add row window")

        self.wnd_role_add = wnd_role_add
        self.ad = ad
        self.rul = RoleUpdateLogic(ad)

        # Add title top window
        wnd_role_add.title("Role Data Add")

        self.frm_attribute = ctk.CTkFrame(wnd_role_add)
        self.frm_attribute.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_role_code = ctk.CTkLabel(self.frm_attribute, text="Role Code")
        self.lbl_role_code.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_role_code = ctk.CTkEntry(self.frm_attribute)
        self.ent_role_code.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_role_name = ctk.CTkLabel(self.frm_attribute, text="Role Name")
        self.lbl_role_name.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_role_name = ctk.CTkEntry(self.frm_attribute)
        self.ent_role_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_display_order = ctk.CTkLabel(self.frm_attribute, text="Display Order")
        self.lbl_display_order.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self. ent_display_order = ctk.CTkEntry(self.frm_attribute)
        self.ent_display_order.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.chc_rn = ctk.CTkCheckBox(self.frm_attribute, text="RN")
        self.chc_rn.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        # Action Buttons
        self.btn_add = ctk.CTkButton(self.wnd_role_add, text="Add", command=self.handle_add_click)
        self.btn_add.pack(pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(wnd_role_add, text="Exit", command=self.wnd_role_add.destroy)
        self.btn_exit.pack(pady=6, padx=10)

    def handle_add_click(self):
        """Update current record or insert a new one if it does not exist."""
        role_code = self.ent_role_code.get()
        role_name = self.ent_role_name.get()
        if not role_name:
            role_name = role_code
        display_order = self.ent_display_order.get()
        rn = self.chc_rn.get()

        success, message = self.rul.add_role(role_code, role_name, display_order, rn)

        if success:
            CTkMessagebox(title="Information", message=message, icon='info')
            self.ent_role_code.delete(0, 9999)
            self.ent_role_name.delete(0, 9999)
            self.ent_display_order.delete(0, 9999)
            self.chc_rn.deselect()
        else:
            input_warning(self.wnd_role_add, message)
