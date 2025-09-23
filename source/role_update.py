"""This module contains the routines to manage the Role table."""
import logging

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from source.appdata import AppData
from source.window import child_window, set_disabled_checkbox, set_disabled_entry, input_warning

logger = logging.getLogger(__name__)


class RoleUpdate(object):
    """Window to allow user to update Role data using a table."""
    def __init__(self, ad: AppData, wnd_role: ctk.CTkToplevel) -> None:
        """Window to allow user to update Role data in a table."""
        logger.info("Creating Role Table data update window")

        self.wnd_role = wnd_role
        self.ad = ad

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
        self.ent_display_order = []
        self.ent_role_code = []
        self.ent_role_name = []
        self.chc_rn = []

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
        # Validate integer attribute
        for db_r in range(self.ad.md.len('Role')):
            if not self.ent_display_order[db_r].get().isdigit():
                input_warning(self.wnd_role, "Display Order field must be integer!")
                return

        # Check every value to see if it has changed
        number_changes = 0
        for db_r in range(self.ad.md.len('Role')):
            # Propagate Role Code changes to foreign keys in Role Competency and Staff Role tables
            if self.ad.md.get('Role', 'Role Code', db_r) != self.ent_role_code[db_r].get():
                self.ad.master_updated = True
                old = self.ad.md.get('Role', 'Role Code', db_r)
                new = self.ent_role_code[db_r].get()
                self.ad.md.replace('Role Competency', 'Role Code', old, new)
                self.ad.md.replace('Staff Role', 'Role Code', old, new)

            # Update row if it has changed
            if (self.ad.md.get('Role', 'Display Order', db_r) != int(self.ent_display_order[db_r].get())
                    or self.ad.md.get('Role', 'Role Code', db_r) != self.ent_role_code[db_r].get()
                    or self.ad.md.get('Role', 'Role Name', db_r) != self.ent_role_name[db_r].get()
                    or self.ad.md.get('Role', 'RN', db_r) != self.chc_rn[db_r].get()):
                number_changes += 1
                self.ad.master_updated = True
                self.ad.md.update_row('Role', db_r, {'Display Order': int(self.ent_display_order[db_r].get()),
                                                     'Role Code': self.ent_role_code[db_r].get(),
                                                     'Role Name': self.ent_role_name[db_r].get(),
                                                     'RN': self.chc_rn[db_r].get()})

        CTkMessagebox(title="Information", message=f"{number_changes} changes saved", icon='info')

        # Sort table and refresh display
        if number_changes > 0:
            self.ad.md.sort_table('Role')
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
        for i in range(len(self.ent_display_order) - self.ad.md.len('Role')):
            # Remove last row of widgets
            self.ent_display_order[-1].destroy()
            self.ent_display_order.pop()
            self.ent_role_code[-1].destroy()
            self.ent_role_code.pop()
            self.ent_role_name[-1].destroy()
            self.ent_role_name.pop()
            self.chc_rn[-1].destroy()
            self.chc_rn.pop()

        # Re-display table
        self.display_role_table()

    def display_role_table(self):
        """Display widgets for all role records."""
        for db_r in range(self.ad.md.len('Role')):
            self.add_role_to_display(db_r)

    def add_role_to_display(self, db_r):
        if db_r + 1 > len(self.ent_display_order):
            col = 0
            self.ent_display_order.append(ctk.CTkEntry(self.frm_s, width=self.width[col]))
            self.ent_display_order[db_r].grid(row=db_r + 1, column=col, sticky='w')

            col += 1
            self.ent_role_code.append(ctk.CTkEntry(self.frm_s, width=self.width[col]))
            self.ent_role_code[db_r].grid(row=db_r + 1, column=col, sticky='w')

            col += 1
            self.ent_role_name.append(ctk.CTkEntry(self.frm_s, width=self.width[col]))
            self.ent_role_name[db_r].grid(row=db_r + 1, column=col, sticky='w')

            col += 1
            self.chc_rn.append(ctk.CTkCheckBox(self.frm_s,
                                               width=self.width[col] - 2 * int(self.width[col] / 3), text=""))
            self.chc_rn[db_r].grid(row=db_r + 1, column=col, sticky='nsew', padx=int(self.width[col] / 3))

        self.ent_display_order[db_r].delete(0, 9999)
        self.ent_display_order[db_r].insert(0, self.ad.md.get('Role', 'Display Order', db_r))

        self.ent_role_code[db_r].delete(0, 9999)
        self.ent_role_code[db_r].insert(0, self.ad.md.get('Role', 'Role Code', db_r))

        self.ent_role_name[db_r].delete(0, 9999)
        self.ent_role_name[db_r].insert(0, self.ad.md.get('Role', 'Role Name', db_r))

        if self.ad.md.get('Role', 'RN', db_r):
            self.chc_rn[db_r].select()
        else:
            self.chc_rn[db_r].deselect()


class RoleDelete(object):
    """Window to allow user to delete Role data records."""
    def __init__(self, ad: AppData, wnd_role_del: ctk.CTkToplevel) -> None:
        logger.info(f"Creating Role data delete window")

        self.wnd_role_del = wnd_role_del
        self.ad = ad

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
        # Identify selected role code
        role_code = self.cmb_role_code.get()
        if not role_code:
            return
        db_r = self.ad.md.index('Role', 'Role Code', role_code)

        # Warn that dependent rows will be deleted
        rc_cnt = self.ad.md.count('Role Competency', 'Role Code', role_code)
        sr_cnt = self.ad.md.count('Staff Role', 'Role Code', role_code)
        if rc_cnt or sr_cnt:
            warn_text = f"{role_code} is used {rc_cnt} times in Role Competency and {sr_cnt} times in Staff Role"
            msg = CTkMessagebox(title="Dependent Record Warning", message=warn_text,
                                icon='warning', option_1='Delete', option_2='Cancel')
            if msg.get() != 'Delete':
                self.wnd_role_del.grab_set()
                return
            self.wnd_role_del.grab_set()

        # Delete row and dependent rows, note deletes not audited
        self.ad.master_updated = True
        self.ad.md.delete_row('Role', db_r)

        # Delete entries for Role Code in Role Competency table
        if rc_cnt:
            self.ad.md.delete_value('Role Competency', 'Role Code', role_code)

        # Delete entries for Role Code in Staff Role dataframe
        if sr_cnt:
            self.ad.md.delete_value('Staff Role', 'Role Code', role_code)

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

        if not role_code:
            input_warning(self.wnd_role_add, "Role Code field must be set!")
            return
        elif display_order and not str(display_order).isdigit():
            input_warning(self.wnd_role_add, "Display Order field must be an integer!")
            return

        # If display order not set then set it to be after last row
        if not display_order:
            display_order = self.ad.md.get('Role', 'Display Order', self.ad.md.len('Role') - 1) + 1
        else:
            display_order = int(display_order)

        # Find Role Code to update or add a new one
        try:
            self.ad.md.index('Role', 'Role Code', role_code)
        except IndexError:
            self.ad.master_updated = True
            self.ad.md.add_row('Role', {'Role Code': role_code,
                                        'Role Name': role_name,
                                        'Display Order': display_order,
                                        'RN': rn})
            CTkMessagebox(title="Information", message=f"Added {role_code} - {role_name}", icon='info')
        else:
            input_warning(self.wnd_role_add, f"Role Code {role_code} all ready defined!")
