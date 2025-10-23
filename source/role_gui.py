"""This module contains the routines to manage the Role table."""
import logging

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from source.appdata import AppData
from source.role_logic import RoleUpdateLogic
from source.window import child_window, set_disabled_checkbox, set_disabled_entry, input_warning

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

        self.header = ['Display Order', 'Role Code', 'Role Name', 'RN']
        self.width = [90, 90, 250, 90]

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
        number_changes, message = self.rul.save_roles(self.role_widgets)

        if message != f"{number_changes} changes saved":
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
            self.role_widgets[-1]['display_order'].destroy()
            self.role_widgets[-1]['role_code'].destroy()
            self.role_widgets[-1]['role_name'].destroy()
            self.role_widgets[-1]['rn'].destroy()
            self.role_widgets.pop()

        # Re-display table
        self.display_role_table()

    def display_role_table(self):
        """Display widgets for all role records."""
        for db_r in range(self.ad.md.len('Role')):
            self.add_role_to_display(db_r)

    def add_role_to_display(self, db_r):
        if db_r + 1 > len(self.role_widgets):
            self.role_widgets.append({'display_order': ctk.CTkEntry(self.frm_s, width=self.width[0]),
                                      'role_code': ctk.CTkEntry(self.frm_s, width=self.width[1]),
                                      'role_name': ctk.CTkEntry(self.frm_s, width=self.width[2]),
                                      'rn': ctk.CTkCheckBox(self.frm_s,
                                                            width=self.width[3] - 2 * int(self.width[3] / 3),
                                                            text="")})
            self.role_widgets[db_r]['display_order'].grid(row=db_r + 1, column=0, sticky='w')
            self.role_widgets[db_r]['role_code'].grid(row=db_r + 1, column=1, sticky='w')
            self.role_widgets[db_r]['role_name'].grid(row=db_r + 1, column=2, sticky='w')
            self.role_widgets[db_r]['rn'].grid(row=db_r + 1, column=3, sticky='nsew', padx=int(self.width[3] / 3))

        self.role_widgets[db_r]['display_order'].delete(0, 9999)
        self.role_widgets[db_r]['display_order'].insert(0, self.ad.md.get('Role', 'Display Order', db_r))

        self.role_widgets[db_r]['role_code'].delete(0, 9999)
        self.role_widgets[db_r]['role_code'].insert(0, self.ad.md.get('Role', 'Role Code', db_r))

        self.role_widgets[db_r]['role_name'].delete(0, 9999)
        self.role_widgets[db_r]['role_name'].insert(0, self.ad.md.get('Role', 'Role Name', db_r))

        if self.ad.md.get('Role', 'RN', db_r):
            self.role_widgets[db_r]['rn'].select()
        else:
            self.role_widgets[db_r]['rn'].deselect()


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

    # noinspection PyUnusedLocal
    def refresh_role(self, event):
        """Display the role record selected."""
        # Identify selected role code
        role_code = self.cmb_role_code.get()
        db_r = self.ad.md.index('Role', 'Role Code', role_code)

        set_disabled_entry(self.ent_role_name, self.ad.md.get('Role', 'Role Name', db_r))
        set_disabled_entry(self.ent_display_order, self.ad.md.get('Role', 'Display Order', db_r))
        set_disabled_checkbox(self.chc_rn, self.ad.md.get('Role', 'RN', db_r))

    def handle_delete_click(self):
        """Delete current record."""
        role_code = self.cmb_role_code.get()
        success, message = self.rul.delete_role(role_code)

        if not success:
            if message != "No role code selected.":
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
        display_order = self.ent_display_order.get()
        rn = self.chc_rn.get()

        success, message = self.rul.add_role(role_code, role_name, display_order, rn)

        if success:
            CTkMessagebox(title="Information", message=message, icon='info')
        else:
            input_warning(self.wnd_role_add, message)
