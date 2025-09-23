"""This module contains the routines to manage the Service table."""
import logging

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from source.appdata import AppData
from source.window import child_window, set_disabled_entry, input_warning

logger = logging.getLogger(__name__)


class ServiceUpdate(object):
    """Window to allow user to update Service data using a table."""
    def __init__(self, ad: AppData, wnd_service: ctk.CTkToplevel) -> None:
        """Window to allow user to update Service data in a table."""
        logger.info("Creating Service Table data update window")

        self.wnd_service = wnd_service
        self.ad = ad

        # Add title top window
        wnd_service.title("Service Data Update")

        # Create header frame, pad to align with scrollable frame
        self.frm_h = ctk.CTkFrame(wnd_service)
        self.frm_h.pack(padx=6, fill='x', expand=False)

        self.header = ['Service Code', 'Service Name']
        self.width = [90, 250]

        # Create list to hold header labels
        self.lbl_header = []

        # Display header row
        for x in range(len(self.header)):
            self.lbl_header.append(ctk.CTkLabel(self.frm_h, text=self.header[x], height=30, width=self.width[x],
                                                corner_radius=6, fg_color='#00B0F0'))
            self.lbl_header[x].grid(row=0, column=x)

        # Create scrollable frame
        self.frm_s = ctk.CTkScrollableFrame(wnd_service)
        self.frm_s.pack(fill='both', expand=True)

        # Create lists to hold column widgets
        self.ent_service_code = []
        self.ent_service_name = []

        # Display widgets for all service records
        for db_s in range(ad.md.len('Service')):
            self.add_service_to_display(db_s)

        # Create button frame
        self.frm_btn = ctk.CTkFrame(wnd_service)
        self.frm_btn.pack(fill='x', expand=False)

        self.btn_update = ctk.CTkButton(self.frm_btn, text="Save", command=self.handle_save_click)
        self.btn_update.grid(row=0, column=0, pady=6, padx=10)

        self.btn_add = ctk.CTkButton(self.frm_btn, text="Add", command=self.handle_add_click)
        self.btn_add.grid(row=0, column=1, pady=6, padx=10)

        self.btn_add = ctk.CTkButton(self.frm_btn, text="Delete", command=self.handle_delete_click)
        self.btn_add.grid(row=0, column=2, pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(self.frm_btn, text="Exit", command=wnd_service.destroy)
        self.btn_exit.grid(row=0, column=3, pady=6, padx=10)

    def handle_save_click(self):
        """Read all values in table and update the table object if any values
           have changed."""
        # Check every value to see if it has changed
        number_changes = 0
        for db_s in range(self.ad.md.len('Service')):
            # Propagate Service Code changes to foreign keys in Staff Role and Role Competency tables
            if self.ad.md.get('Service', 'Service Code', db_s) != self.ent_service_code[db_s].get():
                self.ad.master_updated = True
                old = self.ad.md.get('Service', 'Service Code', db_s)
                new = self.ent_service_code[db_s].get()
                self.ad.md.replace('Staff Role', 'Service Code', old, new)
                self.ad.md.replace('Role Competency', 'Service Code', old, new)

            if (self.ad.md.get('Service', 'Service Code', db_s) != self.ent_service_code[db_s].get()
                    or self.ad.md.get('Service', 'Service Name', db_s) != self.ent_service_name[db_s].get()):
                number_changes += 1
                self.ad.master_updated = True
                self.ad.md.update_row('Service', db_s, {'Service Code': self.ent_service_code[db_s].get(),
                                                        'Service Name': self.ent_service_name[db_s].get()})

        CTkMessagebox(title="Information", message=f"{number_changes} changes saved", icon='info')

        # Sort table and redisplay widgets for all service records
        if number_changes > 0:
            self.ad.md.sort_table('Service')
            for db_s in range(self.ad.md.len('Service')):
                self.add_service_to_display(db_s)

    def handle_add_click(self):
        """Prompt user for row to be added."""
        # Invoke function to add row to table
        child_window(ServiceAdd, self.ad, self.wnd_service)

        # Display widgets for all service records
        for db_s in range(self.ad.md.len('Service')):
            self.add_service_to_display(db_s)

    def handle_delete_click(self):
        # Call window to delete services
        child_window(ServiceDelete, self.ad, self.wnd_service)

        # Remove a row from the table for each deleted record
        for i in range(len(self.ent_service_code) - self.ad.md.len('Service')):
            # Remove last row of widgets
            self.ent_service_code[-1].destroy()
            self.ent_service_code.pop()
            self.ent_service_name[-1].destroy()
            self.ent_service_name.pop()

        # Display widgets for all service records
        for db_s in range(self.ad.md.len('Service')):
            self.add_service_to_display(db_s)

    def add_service_to_display(self, db_s):
        if db_s + 1 > len(self.ent_service_code):
            col = 0
            self.ent_service_code.append(ctk.CTkEntry(self.frm_s, width=self.width[col]))
            self.ent_service_code[db_s].grid(row=db_s + 1, column=col, sticky='w')

            col += 1
            self.ent_service_name.append(ctk.CTkEntry(self.frm_s, width=self.width[col]))
            self.ent_service_name[db_s].grid(row=db_s + 1, column=col, sticky='w')

        self.ent_service_code[db_s].delete(0, 9999)
        self.ent_service_code[db_s].insert(0, self.ad.md.get('Service', 'Service Code', db_s))

        self.ent_service_name[db_s].delete(0, 9999)
        self.ent_service_name[db_s].insert(0, self.ad.md.get('Service', 'Service Name', db_s))


class ServiceDelete(object):
    """Window to allow user to delete Service data records."""
    def __init__(self, ad: AppData, wnd_service_del: ctk.CTkToplevel) -> None:
        logger.info(f"Creating Service data delete window")

        self.wnd_service_del = wnd_service_del
        self.ad = ad

        # Add title top window
        wnd_service_del.title("Service Data Delete")

        self.frm_attribute = ctk.CTkFrame(wnd_service_del)
        self.frm_attribute.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_service_code = ctk.CTkLabel(self.frm_attribute, text="Service Code")
        self.lbl_service_code.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_service_code = ctk.CTkComboBox(self.frm_attribute, state='readonly',
                                                values=ad.md.get_list('Service', 'Service Code'),
                                                command=self.refresh_service)
        self.cmb_service_code.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_service_name = ctk.CTkLabel(self.frm_attribute, text="Service Name")
        self.lbl_service_name.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_service_name = ctk.CTkEntry(self.frm_attribute, state='disabled')
        self.ent_service_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        # Action Buttons
        self.btn_delete = ctk.CTkButton(wnd_service_del, text="Delete", command=self.handle_delete_click)
        self.btn_delete.pack(pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(wnd_service_del, text="Exit", command=self.wnd_service_del.destroy)
        self.btn_exit.pack(pady=6, padx=10)

    # noinspection PyUnusedLocal
    def refresh_service(self, event):
        """Display the service record selected."""
        # Identify selected service code
        service_code = self.cmb_service_code.get()
        db_s = self.ad.md.index('Service', 'Service Code', service_code)
        set_disabled_entry(self.ent_service_name, self.ad.md.get('Service', 'Service Name', db_s))

    def handle_delete_click(self):
        """Delete current record."""
        # Identify selected service code
        service_code = self.cmb_service_code.get()
        if not service_code:
            return
        db_s = self.ad.md.index('Service', 'Service Code', service_code)

        # Warn that dependent rows will be deleted
        sr_cnt = self.ad.md.count('Staff Role', 'Service Code', service_code)
        rc_cnt = self.ad.md.count('Role Competency', 'Service Code', service_code)
        if rc_cnt or sr_cnt:
            warn_text = f"{service_code} is used {sr_cnt} times in Staff Role and {rc_cnt} times in Role Competency"
            win_msg = CTkMessagebox(title="Dependent Record Warning", message=warn_text,
                                    icon='warning', option_1='Delete', option_2='Cancel')
            if win_msg.get() != 'Delete':
                self.wnd_service_del.grab_set()
                return
            self.wnd_service_del.grab_set()

        # Delete row and dependent rows, note deletes not audited
        self.ad.master_updated = True
        self.ad.md.delete_row('Service', db_s)

        # Delete entries for Service Code in Staff Role table
        if rc_cnt:
            self.ad.md.delete_value('Staff Role', 'Service Code', service_code)

        # Delete entries for Service Code in Role Competency table
        if rc_cnt:
            self.ad.md.delete_value('Role Competency', 'Service Code', service_code)

        # Clear widgets
        self.cmb_service_code.set('')
        self.cmb_service_code.configure(values=self.ad.md.get_list('Service', 'Service Code'))
        set_disabled_entry(self.ent_service_name, '')


class ServiceAdd(object):
    """Window to allow user to add Service data record."""
    def __init__(self, ad: AppData, wnd_service_add: ctk.CTkToplevel) -> None:
        logger.info(f"Creating Service data add row window")

        self.wnd_service_add = wnd_service_add
        self.ad = ad

        # Add title to window
        wnd_service_add.title("Service Data Add")

        self.frm_attribute = ctk.CTkFrame(wnd_service_add)
        self.frm_attribute.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_service_code = ctk.CTkLabel(self.frm_attribute, text="Service Code")
        self.lbl_service_code.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_service_code = ctk.CTkEntry(self.frm_attribute)
        self.ent_service_code.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_service_name = ctk.CTkLabel(self.frm_attribute, text="Service Name")
        self.lbl_service_name.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_service_name = ctk.CTkEntry(self.frm_attribute)
        self.ent_service_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        # Action Buttons
        self.btn_add = ctk.CTkButton(wnd_service_add, text="Add", command=self.handle_add_click)
        self.btn_add.pack(pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(wnd_service_add, text="Exit", command=wnd_service_add.destroy)
        self.btn_exit.pack(pady=6, padx=10)

    def handle_add_click(self):
        """Add new record if it does not exist."""
        service_code = self.ent_service_code.get()
        service_name = self.ent_service_name.get()

        if not service_code:
            input_warning(self.wnd_service_add, "Service Code field must be set!")
            return

        # Find Service Code to update or add a new one
        try:
            self.ad.md.index('Service', 'Service Code', service_code)
        except IndexError:
            self.ad.master_updated = True
            self.ad.md.add_row('Service', {'Service Code': service_code, 'Service Name': service_name})
            CTkMessagebox(title="Information", message=f"Added {service_code} - {service_name}", icon='info')
        else:
            input_warning(self.wnd_service_add, f"Service Code {service_code} all ready defined!")
