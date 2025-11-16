"""This module contains the routines to manage the Staff table."""
import logging
import re

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from source.appdata import AppData
from source.staff_logic import StaffLogic
from source.staff_role_gui import StaffRoleUpdate
from source.window import (child_window, set_disabled_checkbox,
                           set_disabled_entry, input_warning, parse_date, date_to_string)

logger = logging.getLogger(__name__)


class StaffUpdate(object):
    """Window to allow user to update Staff data. The data is presented as a table."""
    def __init__(self, ad: AppData, wnd_staff: ctk.CTkToplevel) -> None:
        """Window to allow user to update Staff data."""
        logger.info("Creating Staff Grid data update window")

        self.wnd_staff = wnd_staff
        self.ad = ad
        self.sl = StaffLogic(ad)

        # Add title top window
        self.wnd_staff.title("Staff Data Update")

        # Create data update frame on left of window
        self.frm_table = ctk.CTkFrame(self.wnd_staff)
        self.frm_table.pack(fill='both', side='left', expand=True)

        # Create frame for staff lookup filters on right of window
        self.frm_lookup = ctk.CTkFrame(self.wnd_staff)
        self.frm_lookup.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_staff_count = ctk.CTkLabel(self.frm_lookup, text=f"X of Y staff displayed")
        self.lbl_staff_count.grid(row=row, column=0, columnspan=2, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_name_filter = ctk.CTkLabel(self.frm_lookup, text="Name Filter")
        self.lbl_name_filter.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_name_filter = ctk.CTkEntry(self.frm_lookup)
        self.ent_name_filter.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        self.ent_name_filter.bind("<Return>", command=self.apply_filters)

        row += 1
        self.lbl_no_role = ctk.CTkLabel(self.frm_lookup, text="No Role")
        self.lbl_no_role.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.chc_no_role_filter = ctk.CTkCheckBox(self.frm_lookup, text="")
        self.chc_no_role_filter.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        self.chc_no_role_filter.select()
        self.chc_no_role_filter.bind("<Button-1>", command=self.apply_filters)

        row += 1
        self.lbl_service_filter = ctk.CTkLabel(self.frm_lookup, text="Service Codes")
        self.lbl_service_filter.grid(row=row, column=0, pady=1, padx=10, sticky='e')
        self.chc_service_filter = []
        row -= 1
        for db_sc, service_code in enumerate(ad.md.get_list('Service', 'Service Code')):
            row += 1
            self.chc_service_filter.append(ctk.CTkCheckBox(self.frm_lookup, text=service_code))
            self.chc_service_filter[db_sc].grid(row=row, column=1, pady=1, padx=10, sticky='w')
            self.chc_service_filter[db_sc].bind("<Button-1>", command=self.apply_filters)
            if service_code != 'LEFT':
                self.chc_service_filter[db_sc].select()

        row += 1
        self.lbl_role_filter = ctk.CTkLabel(self.frm_lookup, text="Roles")
        self.lbl_role_filter.grid(row=row, column=0, pady=1, padx=10, sticky='e')
        self.chc_role_filter = []
        row -= 1
        for db_r, role_code in enumerate(ad.md.get_list('Role', 'Role Code')):
            row += 1
            role_name = self.ad.md.get('Role', 'Role Name', db_r)
            self.chc_role_filter.append(ctk.CTkCheckBox(self.frm_lookup, text=role_name))
            if self.ad.md.count('Staff Role', 'Role Code', role_code) > 0:
                self.chc_role_filter[db_r].grid(row=row, column=1, pady=1, padx=10, sticky='w')
                self.chc_role_filter[db_r].bind("<Button-1>", command=self.apply_filters)
                self.chc_role_filter[db_r].select()

        row += 1
        self.btn_clear_all = ctk.CTkButton(self.frm_lookup, width=80, text="Clear All", command=self.clear_all)
        self.btn_clear_all.grid(row=row, column=0, pady=6, padx=10, sticky='e')

        self.btn_set_all = ctk.CTkButton(self.frm_lookup, width=80, text="Set All", command=self.set_all)
        self.btn_set_all.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.btn_clear_rn = ctk.CTkButton(self.frm_lookup, width=80, text="Clear RN", command=self.clear_rn)
        self.btn_clear_rn.grid(row=row, column=0, pady=6, padx=10, sticky='e')

        self.btn_set_rn = ctk.CTkButton(self.frm_lookup, width=80, text="Set RN", command=self.set_rn)
        self.btn_set_rn.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.btn_clear_hca = ctk.CTkButton(self.frm_lookup, width=80, text="Clear HCA", command=self.clear_hca)
        self.btn_clear_hca.grid(row=row, column=0, pady=6, padx=10, sticky='e')

        self.btn_set_hca = ctk.CTkButton(self.frm_lookup, width=80, text="Set HCA", command=self.set_hca)
        self.btn_set_hca.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        # Create header frame, pad to align with scrollable frame
        self.frm_h = ctk.CTkFrame(self.frm_table)
        self.frm_h.pack(padx=6, fill='x', expand=False)

        self.header = ['Staff Name', 'Start Date', 'Supervisor', 'Assessor', 'Roles']
        self.width = [250, 90, 90, 90, 180]

        # Create list to hold header labels
        self.lbl_header = []

        # Display header row
        for x in range(len(self.header)):
            self.lbl_header.append(ctk.CTkLabel(self.frm_h, text=self.header[x], height=30, width=self.width[x],
                                                corner_radius=6, fg_color='#00B0F0'))
            self.lbl_header[x].grid(row=0, column=x)

        # Create scrollable frame for staff table
        self.frm_s = ctk.CTkScrollableFrame(self.frm_table)
        self.frm_s.pack(fill='both', expand=True)

        # Create lists to hold column widgets
        self.ent_staff_name = []
        self.ent_start_date = []
        self.chc_practice_supervisor = []
        self.chc_practice_assessor = []
        self.lbl_roles = []

        # Apply default filters to staff to be displayed
        self.db_s_list = []
        self.apply_filters()

        # Create button frame
        self.frm_btn = ctk.CTkFrame(self.frm_table)
        self.frm_btn.pack(fill='x', expand=False)

        self.btn_update = ctk.CTkButton(self.frm_btn, text="Save", command=self.handle_save_click)
        self.btn_update.grid(row=0, column=0, pady=6, padx=10)

        self.btn_add = ctk.CTkButton(self.frm_btn, text="Add", command=self.handle_add_click)
        self.btn_add.grid(row=0, column=1, pady=6, padx=10)

        self.btn_delete = ctk.CTkButton(self.frm_btn, text="Delete", command=self.handle_delete_click)
        self.btn_delete.grid(row=0, column=2, pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(self.frm_btn, text="Exit", command=self.wnd_staff.destroy)
        self.btn_exit.grid(row=0, column=3, pady=6, padx=10)

    def set_rn(self):
        for db_r, role_code in enumerate(self.ad.md.get_list('Role', 'Role Code')):
            if self.ad.md.get('Role', 'RN', db_r) and self.ad.md.count('Staff Role', 'Role Code', role_code) > 0:
                self.chc_role_filter[db_r].select()
        self.apply_filters()

    def clear_rn(self):
        for db_r, role_code in enumerate(self.ad.md.get_list('Role', 'Role Code')):
            if self.ad.md.get('Role', 'RN', db_r):
                self.chc_role_filter[db_r].deselect()
        self.apply_filters()

    def set_hca(self):
        for db_r, role_code in enumerate(self.ad.md.get_list('Role', 'Role Code')):
            if not self.ad.md.get('Role', 'RN', db_r) and self.ad.md.count('Staff Role', 'Role Code', role_code) > 0:
                self.chc_role_filter[db_r].select()
        self.apply_filters()

    def clear_hca(self):
        for db_r, role_code in enumerate(self.ad.md.get_list('Role', 'Role Code')):
            if not self.ad.md.get('Role', 'RN', db_r):
                self.chc_role_filter[db_r].deselect()
        self.apply_filters()

    def set_all(self):
        self.chc_no_role_filter.select()
        for db_sc, service_code in enumerate(self.ad.md.get_list('Service', 'Service Code')):
            self.chc_service_filter[db_sc].select()
        for db_r, role_code in enumerate(self.ad.md.get_list('Role', 'Role Code')):
            if self.ad.md.count('Staff Role', 'Role Code', role_code) > 0:
                self.chc_role_filter[db_r].select()
        self.apply_filters()

    def clear_all(self):
        self.ent_name_filter.delete(0, 9999)
        self.chc_no_role_filter.deselect()
        for db_sc, service_code in enumerate(self.ad.md.get_list('Service', 'Service Code')):
            self.chc_service_filter[db_sc].deselect()
        for db_r, role_code in enumerate(self.ad.md.get_list('Role', 'Role Code')):
            self.chc_role_filter[db_r].deselect()
        self.apply_filters()

    def apply_filters(self, event: str = None) -> None:
        logger.debug(f"apply_filters called with event {event}")
        # Remove every thing except letters and spaces from name filter string
        name_filter = self.ent_name_filter.get()
        if name_filter:
            name_filter = re.sub(r"[^a-zA-Z -']", '', name_filter).strip()
            self.ent_name_filter.delete(0, 9999)
            self.ent_name_filter.insert(0, name_filter)

        # Create list of the service code filters
        service_filter = []
        for db_sc, service_code in enumerate(self.ad.md.get_list('Service', 'Service Code')):
            if self.chc_service_filter[db_sc].get():
                service_filter.append(service_code)

        # Create list of the role filters
        role_filter = []
        for db_r, role_code in enumerate(self.ad.md.get_list('Role', 'Role Code')):
            if self.chc_role_filter[db_r].get():
                role_filter.append(role_code)

        self.db_s_list = self.sl.apply_filters(self.ent_name_filter.get(),
                                               self.chc_no_role_filter.get(), service_filter, role_filter)

        self.display_staff_table()

    def handle_save_click(self):
        """Read all values in table and update the table object if any values have changed."""
        # Validate date attribute
        for s, db_s in enumerate(self.db_s_list):
            start_date = self.ent_start_date[s].get()
            if start_date and not parse_date(start_date):
                input_warning(self.wnd_staff, f"Start Date {start_date} is not a valid date!")
                return

        staff_widgets = []
        for s, db_s in enumerate(self.db_s_list):
            staff_widgets.append({'Staff Name': self.ent_staff_name[s].get(),
                                  'Start Date': self.ent_start_date[s].get(),
                                  'Practice Supervisor': self.chc_practice_supervisor[s].get(),
                                  'Practice Assessor': self.chc_practice_assessor[s].get()})

        number_changes, message = self.sl.save_staff(staff_widgets, self.db_s_list)

        CTkMessagebox(title="Information", message=message, icon='info')

        # Sort table and refresh redisplay
        if number_changes > 0:
            self.apply_filters()

    def handle_add_click(self):
        """Prompt user for row to be added."""
        # Invoke function to add row to table
        child_window(StaffAdd, self.ad, self.wnd_staff)

        # Refresh table, this will add the extra row
        self.apply_filters()

    def handle_delete_click(self):
        # Call window to delete competencies
        child_window(StaffDelete, self.ad, self.wnd_staff)

        # Re-display table
        self.apply_filters()

    def display_staff_table(self):
        """Display widgets for all staff records."""

        for s, db_s in enumerate(self.db_s_list):
            self.add_staff_to_display(s, db_s)

        # Remove any rows from the end of table that have not been populated
        for i in range(len(self.ent_staff_name) - len(self.db_s_list)):
            # Remove last row of widgets
            self.ent_staff_name[-1].destroy()
            self.ent_staff_name.pop()
            self.ent_start_date[-1].destroy()
            self.ent_start_date.pop()
            self.chc_practice_supervisor[-1].destroy()
            self.chc_practice_supervisor.pop()
            self.chc_practice_assessor[-1].destroy()
            self.chc_practice_assessor.pop()
            self.lbl_roles[-1].destroy()
            self.lbl_roles.pop()

        self.lbl_staff_count.configure(text=f"{len(self.db_s_list)} of {self.ad.md.len('Staff')} staff displayed")

    def add_staff_to_display(self, s, db_s):
        if s + 1 > len(self.ent_staff_name):
            col = 0
            self.ent_staff_name.append(ctk.CTkEntry(self.frm_s, width=self.width[col]))
            self.ent_staff_name[s].grid(row=s + 1, column=col, sticky='w')

            col += 1
            self.ent_start_date.append(ctk.CTkEntry(self.frm_s, width=self.width[col]))
            self.ent_start_date[s].grid(row=s + 1, column=col, sticky='w')

            col += 1
            self.chc_practice_supervisor.append(ctk.CTkCheckBox(self.frm_s,
                                                                width=self.width[col] - 2 * int(self.width[col] / 3),
                                                                text=""))
            self.chc_practice_supervisor[s].grid(row=s + 1, column=col,
                                                 sticky='nsew', padx=int(self.width[col] / 3))

            col += 1
            self.chc_practice_assessor.append(ctk.CTkCheckBox(self.frm_s,
                                                              width=self.width[col] - 2 * int(self.width[col] / 3),
                                                              text=""))
            self.chc_practice_assessor[s].grid(row=s + 1, column=col,
                                               sticky='nsew', padx=int(self.width[col] / 3))

            col += 1
            self.lbl_roles.append(ctk.CTkLabel(self.frm_s, width=self.width[col], height=24,
                                               text_color='#808080', fg_color='#FFFFFF', anchor='w'))
            self.lbl_roles[s].grid(row=s + 1, column=col, sticky='w', pady=2)
            self.lbl_roles[s].bind('<Button-1>', self.handel_role_click)

        staff_name = self.ad.md.get('Staff', 'Staff Name', db_s)

        self.ent_staff_name[s].delete(0, 9999)
        self.ent_staff_name[s].insert(0, staff_name)

        self.ent_start_date[s].delete(0, 9999)
        self.ent_start_date[s].insert(0, date_to_string(self.ad.md.get('Staff', 'Start Date', db_s)))

        if self.ad.md.get('Staff', 'Practice Supervisor', db_s):
            self.chc_practice_supervisor[s].select()
        else:
            self.chc_practice_supervisor[s].deselect()

        if self.ad.md.get('Staff', 'Practice Assessor', db_s):
            self.chc_practice_assessor[s].select()
        else:
            self.chc_practice_assessor[s].deselect()

        roles = ' '
        for service_code in self.ad.md.get_list('Service', 'Service Code'):
            db_sr = self.ad.md.find_two('Staff Role', service_code, 'Service Code', staff_name, 'Staff Name')
            if db_sr > -1:
                role = self.ad.md.get('Staff Role', 'Role Code', db_sr)
                roles += service_code + ' ' + role + ', '
        self.lbl_roles[s].configure(text=roles[:-2])

    def handel_role_click(self, event):
        logger.debug(f"handel_role_click from event widget [{event.widget}]")
        # Extract label number from widget
        label_num_search = re.search(r'ctklabel(\d+)?', str(event.widget))
        if not label_num_search:
            logger.error(f"Failed to extract label number from event widget [{event.widget}]")
            return

        # First label has no number
        if not label_num_search.group(1):
            s = 0
        else:
            s = int(label_num_search.group(1)) - 1
        db_s = self.db_s_list[s]
        staff_name = self.ad.md.get('Staff', 'Staff Name', db_s)
        child_window(StaffRoleUpdate, self.ad, self.wnd_staff, staff_name)

        roles = ' '
        for service_code in self.ad.md.get_list('Service', 'Service Code'):
            db_sr = self.ad.md.find_two('Staff Role', service_code, 'Service Code', staff_name, 'Staff Name')
            if db_sr > -1:
                role = self.ad.md.get('Staff Role', 'Role Code', db_sr)
                roles += service_code + ' ' + role + ', '
        self.lbl_roles[s].configure(text=roles[:-2])


class StaffDelete(object):
    """Window to allow user to delete Staff data records."""
    def __init__(self, ad: AppData, wnd_staff_del: ctk.CTkToplevel) -> None:
        logger.info(f"Creating Staff Data Delete window")

        self.wnd_staff_del = wnd_staff_del
        self.ad = ad
        self.sl = StaffLogic(ad)

        # Add title top window
        wnd_staff_del.title("Staff Data Delete")

        self.frm_attribute = ctk.CTkFrame(wnd_staff_del)
        self.frm_attribute.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_staff_name = ctk.CTkLabel(self.frm_attribute, text="Staff Name")
        self.lbl_staff_name.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_staff_name = ctk.CTkComboBox(self.frm_attribute, state='readonly',
                                              values=ad.md.get_list('Staff', 'Staff Name'), command=self.refresh_staff)
        self.cmb_staff_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_start_date = ctk.CTkLabel(self.frm_attribute, text="Start Date")
        self.lbl_start_date.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_start_date = ctk.CTkEntry(self.frm_attribute, state='disabled')
        self.ent_start_date.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.chc_practice_supervisor = ctk.CTkCheckBox(self.frm_attribute, text="Practice Supervisor", state='disabled')
        self.chc_practice_supervisor.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.chc_practice_assessor = ctk.CTkCheckBox(self.frm_attribute, text="Practice Assessor", state='disabled')
        self.chc_practice_assessor.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        # Create lookup frame for name filter
        self.frm_lookup = ctk.CTkFrame(wnd_staff_del)
        self.frm_lookup.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_name_filter = ctk.CTkLabel(self.frm_lookup, text="Name Filter")
        self.lbl_name_filter.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_name_filter = ctk.CTkEntry(self.frm_lookup)
        self.ent_name_filter.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.btn_name_filter = ctk.CTkButton(self.frm_lookup, text="Apply Filter", command=self.filter_names)
        self.btn_name_filter.grid(row=row, column=0, columnspan=2, pady=6, padx=10)

        # Action Buttons
        self.btn_delete = ctk.CTkButton(wnd_staff_del, text="Delete", command=self.handle_delete_click)
        self.btn_delete.pack(pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(wnd_staff_del, text="Exit", command=wnd_staff_del.destroy)
        self.btn_exit.pack(pady=6, padx=10)

    # noinspection PyUnusedLocal
    def refresh_staff(self, event):
        """Display the staff record selected."""
        # Identify selected staff
        staff_name = self.cmb_staff_name.get()
        db_s = self.ad.md.index('Staff', 'Staff Name', staff_name)

        set_disabled_entry(self.ent_start_date, date_to_string(self.ad.md.get('Staff', 'Start Date', db_s)))
        set_disabled_checkbox(self.chc_practice_supervisor, self.ad.md.get('Staff', 'Practice Supervisor', db_s))
        set_disabled_checkbox(self.chc_practice_assessor, self.ad.md.get('Staff', 'Practice Assessor', db_s))

    def handle_delete_click(self):
        """Delete current record."""
        staff_name = self.cmb_staff_name.get()

        success, warning, message = self.sl.delete_staff(staff_name)

        if not success:
            if warning:
                msg = CTkMessagebox(title="Dependent Record Warning", message=message,
                                    icon='warning', option_1='Delete', option_2='Cancel')
                if msg.get() == 'Cancel':
                    self.wnd_staff_del.grab_set()
                    return
                self.wnd_staff_del.grab_set()
                self.sl.delete_staff_with_dependents(staff_name)

        # Clear widgets
        self.cmb_staff_name.set('')
        self.cmb_staff_name.configure(values=self.ad.md.get_list('Staff', 'Staff Name'))
        set_disabled_entry(self.ent_start_date, '')
        set_disabled_checkbox(self.chc_practice_supervisor, 0)
        set_disabled_checkbox(self.chc_practice_assessor, 0)

    def filter_names(self):
        """Filter the names in the Staff Name drop down to those that match
           the filter entered by the user."""
        name_filter = self.ent_name_filter.get()
        if name_filter:
            # Remove every thing except letters and spaces from filter string
            name_filter = re.sub(r'[^a-zA-Z -]', '', name_filter).strip()
            self.ent_name_filter.delete(0, 9999)
            self.ent_name_filter.insert(0, name_filter)
            filter_name_lst = []
            for staff_name in self.ad.md.get_list('Staff', 'Staff Name'):
                if re.search(name_filter, staff_name, re.IGNORECASE):
                    filter_name_lst.append(staff_name)
            self.cmb_staff_name.configure(values=filter_name_lst)
        else:
            self.cmb_staff_name.configure(values=self.ad.md.get_list('Staff', 'Staff Name'))


class StaffAdd(object):
    """Window to allow user to add a single Staff data record."""
    def __init__(self, ad: AppData, wnd_staff_add: ctk.CTkToplevel) -> None:

        logger.info(f"Creating Staff data add row window")

        self.wnd_staff_add = wnd_staff_add
        self.ad = ad
        self.sl = StaffLogic(ad)

        # Add title top window
        wnd_staff_add.title("Staff Data Add")

        self.frm_attribute = ctk.CTkFrame(wnd_staff_add)
        self.frm_attribute.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_staff_name = ctk.CTkLabel(self.frm_attribute, text="Staff Name")
        self.lbl_staff_name.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_staff_name = ctk.CTkEntry(self.frm_attribute)
        self.ent_staff_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_start_date = ctk.CTkLabel(self.frm_attribute, text="Start Date")
        self.lbl_start_date.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_start_date = ctk.CTkEntry(self.frm_attribute)
        self.ent_start_date.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.chc_practice_supervisor = ctk.CTkCheckBox(self.frm_attribute, text="Practice Supervisor")
        self.chc_practice_supervisor.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.chc_practice_assessor = ctk.CTkCheckBox(self.frm_attribute, text="Practice Assessor")
        self.chc_practice_assessor.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        # Action Buttons
        self.btn_add = ctk.CTkButton(wnd_staff_add, text="Add", command=self.handle_add_click)
        self.btn_add.pack(pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(wnd_staff_add, text="Exit", command=wnd_staff_add.destroy)
        self.btn_exit.pack(pady=6, padx=10)

    def handle_add_click(self):
        """Update current record or insert a new one if it does not exist."""
        staff_name = self.ent_staff_name.get()
        start_date = self.ent_start_date.get()
        practice_supervisor = self.chc_practice_supervisor.get()
        practice_assessor = self.chc_practice_assessor.get()

        success, staff_name, message = self.sl.add_staff(staff_name, start_date, practice_supervisor, practice_assessor)

        if success:
            self.ent_staff_name.delete(0, 9999)
            self.ent_staff_name.insert(0, staff_name)

            # Open window to add roles for the new staff member
            child_window(StaffRoleUpdate, self.ad, self.wnd_staff_add, re.sub(' +', ' ', staff_name.strip()))
            CTkMessagebox(title="Information", message=message, icon='info')
            self.ent_staff_name.delete(0, 9999)
            self.ent_start_date.delete(0, 9999)
            self.chc_practice_supervisor.deselect()
            self.chc_practice_assessor.deselect()
        else:
            input_warning(self.wnd_staff_add, message)


class StaffAssessorUpdate:
    """Window to allow user to update Practice Assessor status for a single Staff data record."""
    def __init__(self, ad: AppData, wnd_staff_assessor: ctk.CTkToplevel, staff_name: str) -> None:
        logger.info(f"Creating Staff Assessor Update window for Staff Name {staff_name}")
        wnd_staff_assessor.title("Practice Assessor Update")

        self.wnd_staff_assessor = wnd_staff_assessor
        self.ad = ad
        self.staff_name = staff_name
        self.db_s = self.ad.md.index('Staff', 'Staff Name', staff_name)

        self.frm_attribute = ctk.CTkFrame(wnd_staff_assessor)
        self.frm_attribute.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_staff_name = ctk.CTkLabel(self.frm_attribute, text="Staff Name")
        self.lbl_staff_name.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_staff_name = ctk.CTkEntry(self.frm_attribute)
        self.ent_staff_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        self.ent_staff_name.insert(0, staff_name)
        self.ent_staff_name.configure(state='disabled')

        row += 1
        self.chc_practice_assessor = ctk.CTkCheckBox(self.frm_attribute, text="Practice Assessor")
        self.chc_practice_assessor.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        if self.ad.md.get('Staff', 'Practice Assessor', self.db_s):
            self.chc_practice_assessor.select()

        row += 1
        self.chc_practice_supervisor = ctk.CTkCheckBox(self.frm_attribute, text="Practice Supervisor")
        self.chc_practice_supervisor.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        if self.ad.md.get('Staff', 'Practice Supervisor', self.db_s):
            self.chc_practice_supervisor.select()

        # Action Buttons
        self.btn_add = ctk.CTkButton(wnd_staff_assessor, text="Update", command=self.handle_update_click)
        self.btn_add.pack(pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(wnd_staff_assessor, text="Exit", command=wnd_staff_assessor.destroy)
        self.btn_exit.pack(pady=6, padx=10)

    def handle_update_click(self):
        new_practice_assessor = self.chc_practice_assessor.get()
        old_practice_assessor = self.ad.md.get('Staff', 'Practice Assessor', self.db_s)
        new_practice_supervisor = self.chc_practice_supervisor.get()
        old_practice_supervisor = self.ad.md.get('Staff', 'Practice Supervisor', self.db_s)
        if new_practice_assessor != old_practice_assessor or new_practice_supervisor != old_practice_supervisor:
            self.ad.md.update_row('Staff', self.db_s,
                                  {'Practice Assessor': new_practice_assessor,
                                   'Practice Supervisor': new_practice_supervisor})
            self.ad.master_updated = True

        self.wnd_staff_assessor.destroy()
