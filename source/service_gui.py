"""This module contains the GUI routines to manage the Service table."""
import logging
from typing import Any

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from source.appdata import AppData
from source.service_logic import ServiceLogic
from source.window import child_window, set_disabled_entry, input_warning, widget_dict_values

logger = logging.getLogger(__name__)


class ServiceUpdate(object):
    """Window to allow user to update Service data using a table."""
    def __init__(self, ad: AppData, wnd_service: ctk.CTkToplevel) -> None:
        """Window to allow user to update Service data in a table."""
        logger.info("Creating Service Table data update window")

        self.wnd_service = wnd_service
        self.ad = ad
        self.sl = ServiceLogic(ad)

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
        self.service_widgets = []

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
        service_values = widget_dict_values(self.service_widgets)
        number_changes = self.sl.save_services(service_values)
        CTkMessagebox(title="Information", message=f"{number_changes} changes saved", icon='info')

        # Sort table and redisplay widgets for all service records
        if number_changes > 0:
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
        for i in range(len(self.service_widgets) - self.ad.md.len('Service')):
            # Remove last row of widgets
            self.service_widgets[-1]['code'].destroy()
            self.service_widgets[-1]['name'].destroy()
            self.service_widgets.pop()

        # Display widgets for all service records
        for db_s in range(self.ad.md.len('Service')):
            self.add_service_to_display(db_s)

    def add_service_to_display(self, db_s: int):
        if db_s + 1 > len(self.service_widgets):
            self.service_widgets.append({'code': ctk.CTkEntry(self.frm_s, width=self.width[0]),
                                         'name': ctk.CTkEntry(self.frm_s, width=self.width[1])})
            self.service_widgets[db_s]['code'].grid(row=db_s + 1, column=0, sticky='w')
            self.service_widgets[db_s]['name'].grid(row=db_s + 1, column=1, sticky='w')

        self.service_widgets[db_s]['code'].delete(0, 9999)
        self.service_widgets[db_s]['code'].insert(0, self.ad.md.get('Service', 'Service Code', db_s))

        self.service_widgets[db_s]['name'].delete(0, 9999)
        self.service_widgets[db_s]['name'].insert(0, self.ad.md.get('Service', 'Service Name', db_s))


class ServiceDelete(object):
    """Window to allow user to delete Service data records."""
    def __init__(self, ad: AppData, wnd_service_del: ctk.CTkToplevel) -> None:
        logger.info(f"Creating Service data delete window")

        self.wnd_service_del = wnd_service_del
        self.ad = ad
        self.sl = ServiceLogic(ad)

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

    def refresh_service(self, event: Any):
        """Display the service record selected."""
        logger.debug(f"Called with event {event}")
        # Identify selected service code
        service_code = self.cmb_service_code.get()
        db_s = self.ad.md.index('Service', 'Service Code', service_code)
        set_disabled_entry(self.ent_service_name, self.ad.md.get('Service', 'Service Name', db_s))

    def handle_delete_click(self):
        """Delete current record."""
        service_code = self.cmb_service_code.get()
        success, warning, message = self.sl.delete_service(service_code)

        if not success:
            if warning:
                win_msg = CTkMessagebox(title="Dependent Record Warning", message=message,
                                        icon='warning', option_1='Delete', option_2='Cancel')
                if win_msg.get() != 'Delete':
                    self.wnd_service_del.grab_set()
                    return
                self.wnd_service_del.grab_set()
                self.sl.delete_service_with_dependents(service_code)

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
        self.sl = ServiceLogic(ad)

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

        success, message = self.sl.add_service(service_code, service_name)

        if success:
            CTkMessagebox(title="Information", message=message, icon='info')
            self.ent_service_code.delete(0, 9999)
            self.ent_service_name.delete(0, 9999)
        else:
            input_warning(self.wnd_service_add, message)
