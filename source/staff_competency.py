"""This module provides the functions to update Staff Competency records via
   a grid or by directly accessing records."""
import logging
import re

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from tkcalendar import Calendar

from source.appdata import AppData
from source.window import input_warning, date_to_string, parse_date

logger = logging.getLogger(__name__)


class StaffCompetencyUpdate(object):
    """Window to allow user to update Staff Competency record. It can be called
       in two ways; to select and then update multiple records or to update an
       individual record. If the Staff Name and Competency Name are supplied just
       that record will be presented and the search filters and buttons will be
       omitted."""
    def __init__(self,
                 ad: AppData,
                 wnd_staff_competency: ctk.CTkToplevel,
                 inp_staff_name: str = None,
                 inp_competency_name: str = None) -> None:

        self.wnd_staff_competency = wnd_staff_competency
        self.ad = ad
        self.inp_staff_name = inp_staff_name
        self.inp_competency_name = inp_competency_name

        # If Staff Name and Competency Name are supplied we are updating a single record
        if inp_staff_name and inp_competency_name:
            single_record_mode = True
            db_sc = ad.md.find_two('Staff Competency',
                                   inp_staff_name, 'Staff Name',
                                   inp_competency_name, 'Competency Name')
            logger.info(f"Creating Staff Competency Update window for Staff Name {inp_staff_name}"
                        f" and Competency Code {inp_competency_name}")
        else:
            single_record_mode = False
            db_sc = -1
            logger.info("Creating Staff Competency Update window")
        self.single_record_mode = single_record_mode

        # Add title top window
        wnd_staff_competency.title("Staff Competency Update")

        self.frm_attribute = ctk.CTkFrame(wnd_staff_competency)
        self.frm_attribute.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_staff_name = ctk.CTkLabel(self.frm_attribute, text="Staff Name")
        self.lbl_staff_name.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        if single_record_mode:
            self.ent_staff_name = ctk.CTkEntry(self.frm_attribute)
            self.ent_staff_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')
            self.ent_staff_name.insert(0, inp_staff_name)
            self.ent_staff_name.configure(state='disabled')
        else:
            self.cmb_staff_name = ctk.CTkComboBox(self.frm_attribute, state='readonly',
                                                  values=ad.md.get_list('Staff', 'Staff Name'),
                                                  command=self.refresh_competency)
            self.cmb_staff_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_competency_name = ctk.CTkLabel(self.frm_attribute, text="Competency Name")
        self.lbl_competency_name.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        if single_record_mode:
            self.ent_competency_name = ctk.CTkEntry(self.frm_attribute)
            self.ent_competency_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')
            self.ent_competency_name.insert(0, inp_competency_name)
            self.ent_competency_name.configure(state='disabled')
        else:
            self.cmb_competency_name = ctk.CTkComboBox(
                self.frm_attribute,
                state='readonly',
                values=ad.md.get_list('Competency', 'Competency Name'),
                command=self.refresh_competency)
            self.cmb_competency_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_prerequisite_date = ctk.CTkLabel(self.frm_attribute, text="Prerequisite Date")
        self.lbl_prerequisite_date.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_prerequisite_date = ctk.CTkEntry(self.frm_attribute)
        self.ent_prerequisite_date.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        if db_sc > -1:
            self.ent_prerequisite_date.insert(0, date_to_string(ad.md.get('Staff Competency',
                                                                          'Prerequisite Date', db_sc)))

        row += 1
        self.chc_achieved = ctk.CTkCheckBox(self.frm_attribute, text="Achieved")
        self.chc_achieved.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        if db_sc > -1:
            if ad.md.get('Staff Competency', 'Achieved', db_sc):
                self.chc_achieved.select()

        row += 1
        self.lbl_competency_date = ctk.CTkLabel(self.frm_attribute, text="Competency Date")
        self.lbl_competency_date.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_competency_date = ctk.CTkEntry(self.frm_attribute)
        self.ent_competency_date.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        if db_sc > -1:
            self.ent_competency_date.insert(0, date_to_string(ad.md.get('Staff Competency', 'Competency Date', db_sc)))

        row += 1
        self.chc_completed = ctk.CTkCheckBox(self.frm_attribute, text="Completed")
        self.chc_completed.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        if db_sc > -1:
            if ad.md.get('Staff Competency', 'Completed', db_sc):
                self.chc_completed.select()

        row += 1
        self.lbl_notes = ctk.CTkLabel(self.frm_attribute, text="Notes")
        self.lbl_notes.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_notes = ctk.CTkEntry(self.frm_attribute)
        self.ent_notes.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        if db_sc > -1:
            self.ent_notes.insert(0, ad.md.get('Staff Competency', 'Notes', db_sc))

        row += 1
        self.chc_not_required = ctk.CTkCheckBox(self.frm_attribute, text="Force Not Required",
                                                command=self.deselect_required)
        self.chc_not_required.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        if db_sc > -1:
            if ad.md.get('Staff Competency', 'Not Required', db_sc):
                self.chc_not_required.select()

        row += 1
        self.chc_required = ctk.CTkCheckBox(self.frm_attribute, text="Force Required",
                                            command=self.deselect_not_required)
        self.chc_required.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        if db_sc > -1:
            if ad.md.get('Staff Competency', 'Required', db_sc):
                self.chc_required.select()

        # Create lookup frame for filters and calendar
        self.frm_lookup = ctk.CTkFrame(wnd_staff_competency)
        self.frm_lookup.pack(fill='both', side='left', expand=True)

        row = -1

        # If we are not in single record mode setup filters
        if not single_record_mode:
            row += 1
            self.lbl_name_filter = ctk.CTkLabel(self.frm_lookup, text="Name Filter")
            self.lbl_name_filter.grid(row=row, column=0, pady=6, padx=10, sticky='e')
            self.ent_name_filter = ctk.CTkEntry(self.frm_lookup)
            self.ent_name_filter.grid(row=row, column=1, pady=6, padx=10, sticky='w')

            row += 1
            self.lbl_rn_filter = ctk.CTkLabel(self.frm_lookup, text="RN Filter")
            self.lbl_rn_filter.grid(row=row, column=0, pady=6, padx=10, sticky='e')
            self.cmb_rn_filter = ctk.CTkComboBox(self.frm_lookup, state='readonly', values=['', 'RN', 'HCA'])
            self.cmb_rn_filter.grid(row=row, column=1, pady=6, padx=10, sticky='w')

            row += 1
            self.lbl_role_filter = ctk.CTkLabel(self.frm_lookup, text="Role Filter")
            self.lbl_role_filter.grid(row=row, column=0, pady=6, padx=10, sticky='e')
            self.cmb_role_filter = ctk.CTkComboBox(self.frm_lookup, state='readonly',
                                                   values=[''] + ad.md.get_list('Role', 'Role Code'))
            self.cmb_role_filter.grid(row=row, column=1, pady=6, padx=10, sticky='w')

            row += 1
            self.lbl_service_filter = ctk.CTkLabel(self.frm_lookup, text="Service Filter")
            self.lbl_service_filter.grid(row=row, column=0, pady=6, padx=10, sticky='e')
            self.cmb_service_filter = ctk.CTkComboBox(self.frm_lookup, state='readonly',
                                                      values=[''] + ad.md.get_list('Service', 'Service Code'))
            self.cmb_service_filter.grid(row=row, column=1, pady=6, padx=10, sticky='w')

            row += 1
            self.btn_filter = ctk.CTkButton(self.frm_lookup, text="Apply Filters", command=self.apply_filters)
            self.btn_filter.grid(row=row, column=1, pady=6, padx=10)

        # Setup calendar and date update buttons
        row += 1
        self.cal = Calendar(self.frm_lookup, font='Arial 10')
        self.cal.grid(row=row, column=0, columnspan=2, padx=0, pady=6)

        row += 1
        self.lbl_prerequisite = ctk.CTkLabel(self.frm_lookup, text="Prerequisite Date")
        self.lbl_prerequisite.grid(row=row, column=0, columnspan=2, pady=0, padx=10)

        row += 1
        self.btn_set_prerequisite = ctk.CTkButton(self.frm_lookup, text="Set", width=80, command=self.set_prerequisite)
        self.btn_set_prerequisite.grid(row=row, column=0, pady=0, padx=10, sticky='e')

        self.btn_clear_prerequisite = ctk.CTkButton(self.frm_lookup, text="Clear", width=80,
                                                    command=self.clear_prerequisite)
        self.btn_clear_prerequisite.grid(row=row, column=1, pady=0, padx=10, sticky='w')

        row += 1
        self.lbl_competency = ctk.CTkLabel(self.frm_lookup, text="Competency Date")
        self.lbl_competency.grid(row=row, column=0, columnspan=2, pady=2, padx=10)

        row += 1
        self.btn_set_competency = ctk.CTkButton(self.frm_lookup, text="Set", width=80, command=self.set_competency)
        self.btn_set_competency.grid(row=row, column=0, pady=0, padx=10, sticky='e')

        self.btn_clear_competency = ctk.CTkButton(self.frm_lookup, text="Clear", width=80,
                                                  command=self.clear_competency)
        self.btn_clear_competency.grid(row=row, column=1, pady=2, padx=10, sticky='w')

        # Action buttons
        self.btn_update = ctk.CTkButton(wnd_staff_competency, text="Save", command=self.handle_save_click)
        self.btn_update.pack(pady=6, padx=10)

        self.btn_delete = ctk.CTkButton(wnd_staff_competency, text="Delete", command=self.handle_delete_click)
        self.btn_delete.pack(pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(wnd_staff_competency, text="Exit", command=wnd_staff_competency.destroy)
        self.btn_exit.pack(pady=6, padx=10)

    # noinspection PyUnusedLocal
    def refresh_competency(self, event=None):
        """Load the record for the Staff Name and Competency Name entered by the
           user. This will only be called when not in single record mode."""
        staff_name = self.cmb_staff_name.get()
        competency_name = self.cmb_competency_name.get()
        if staff_name:
            db_sc = self.ad.md.find_two('Staff Competency',
                                        staff_name, 'Staff Name',
                                        competency_name, 'Competency Name')
            if db_sc > -1:
                self.ent_prerequisite_date.delete(0, 9999)
                self.ent_prerequisite_date.insert(
                    0, date_to_string(self.ad.md.get('Staff Competency', 'Prerequisite Date', db_sc)))
                self.chc_achieved.deselect()
                if self.ad.md.get('Staff Competency', 'Achieved', db_sc):
                    self.chc_achieved.select()
                self.ent_competency_date.delete(0, 9999)
                self.ent_competency_date.insert(
                    0, date_to_string(self.ad.md.get('Staff Competency', 'Competency Date', db_sc)))
                self.chc_completed.deselect()
                if self.ad.md.get('Staff Competency', 'Completed', db_sc):
                    self.chc_completed.select()
                self.ent_notes.delete(0, 9999)
                self.ent_notes.insert(0, self.ad.md.get('Staff Competency', 'Notes', db_sc))
                self.chc_not_required.deselect()
                if self.ad.md.get('Staff Competency', 'Not Required', db_sc):
                    self.chc_not_required.select()
                self.chc_required.deselect()
                if self.ad.md.get('Staff Competency', 'Required', db_sc):
                    self.chc_required.select()
            else:
                self.ent_prerequisite_date.delete(0, 9999)
                self.chc_achieved.deselect()
                self.ent_competency_date.delete(0, 9999)
                self.chc_completed.deselect()
                self.ent_notes.delete(0, 9999)
                self.chc_not_required.deselect()
                self.chc_required.deselect()

    def apply_filters(self):
        """Apply the filter criteria entered by the user. This will only be
           called when not in single record mode."""
        rn_filter = self.cmb_rn_filter.get()
        role_filter = self.cmb_role_filter.get()

        # If the RN filter it can be inferred from the Role filter
        if not rn_filter and role_filter:
            db_r = self.ad.md.find_one('Role', role_filter, 'Role Code')
            if db_r > -1 and self.ad.md.get('Role', 'RN', db_r) == 1:
                rn_filter = 'RN'
            else:
                rn_filter = 'HCA'

        service_filter = self.cmb_service_filter.get()

        # Filter competency names for RN and service
        if rn_filter or service_filter:
            filter_competency_lst = []
            for db_c in range(self.ad.md.len('Competency')):
                competency_name = self.ad.md.get('Competency', 'Competency Name', db_c)
                if ((not rn_filter
                     or rn_filter == self.ad.md.get('Competency', 'Scope', db_c)
                     or self.ad.md.get('Competency', 'Scope', db_c) == 'BOTH')
                        and (not service_filter
                             or self.ad.md.find_two('Role Competency',
                                                    service_filter, 'Service Code',
                                                    competency_name, 'Competency Name') > -1)):
                    filter_competency_lst.append(competency_name)
            self.cmb_competency_name.configure(values=filter_competency_lst)
            if self.cmb_competency_name.get() not in filter_competency_lst:
                self.cmb_competency_name.set('')
        else:
            self.cmb_competency_name.configure(values=self.ad.md.get_list('Competency', 'Competency Name'))

        # Remove every thing except letters and spaces from name filter string
        name_filter = self.ent_name_filter.get()
        if name_filter:
            name_filter = re.sub(r"[^a-zA-Z -']", '', name_filter).strip()
            self.ent_name_filter.delete(0, 9999)
            self.ent_name_filter.insert(0, name_filter)

        # Filter staff names for RN or role, service and name match
        if rn_filter or role_filter or service_filter or name_filter:
            filter_name_lst = []
            for staff_name in self.ad.md.get_list('Staff', 'Staff Name'):
                rn_match = False
                if not rn_filter:
                    rn_match = True
                else:
                    if rn_filter == 'RN':
                        rn = 1
                    else:
                        rn = 0
                    for db_sr in range(self.ad.md.len('Staff Role')):
                        if self.ad.md.get('Staff Role', 'Staff Name', db_sr) == staff_name:
                            if self.ad.md.find_two('Role',
                                                   self.ad.md.get('Staff Role', 'Role Code', db_sr), 'Role Code',
                                                   rn, 'RN') > -1:
                                rn_match = True
                                break
                if (rn_match
                        and (not role_filter
                             or self.ad.md.find_two('Staff Role',
                                                    staff_name, 'Staff Name',
                                                    role_filter, 'Role Code') > -1)
                        and (not service_filter
                             or self.ad.md.find_two('Staff Role',
                                                    staff_name, 'Staff Name',
                                                    service_filter, 'Service Code') > -1)
                        and (not name_filter
                             or re.search(name_filter, staff_name, re.I))):
                    filter_name_lst.append(staff_name)
            self.cmb_staff_name.configure(values=filter_name_lst)
            if self.cmb_staff_name.get() not in filter_name_lst:
                self.cmb_staff_name.set('')
        else:
            self.cmb_staff_name.configure(values=self.ad.md.get_list('Staff', 'Staff Name'))

    def clear_prerequisite(self):
        """Clear Prerequisite Date."""
        self.chc_achieved.deselect()
        self.ent_prerequisite_date.delete(0, 9999)

    def set_prerequisite(self):
        """Set Prerequisite Date to the date set on the calendar widget."""
        self.chc_achieved.select()
        self.ent_prerequisite_date.delete(0, 9999)
        self.ent_prerequisite_date.insert(0, date_to_string(self.cal.selection_get()))

    def clear_competency(self):
        """Clear Competency Date."""
        self.chc_completed.deselect()
        self.ent_competency_date.delete(0, 9999)

    def set_competency(self):
        """Set Competency Date to the date set on the calendar widget."""
        self.chc_completed.select()
        self.ent_competency_date.delete(0, 9999)
        self.ent_competency_date.insert(0, date_to_string(self.cal.selection_get()))

    def handle_delete_click(self):
        """Delete record, don't need check use in other tables."""
        if self.single_record_mode:
            staff_name = self.inp_staff_name
            competency_name = self.inp_competency_name
        else:
            staff_name = self.cmb_staff_name.get()
            competency_name = self.cmb_competency_name.get()

        if staff_name and competency_name:
            db_sc = self.ad.md.find_two('Staff Competency',
                                        staff_name, 'Staff Name',
                                        competency_name, 'Competency Name')
            if db_sc > -1:
                self.ad.master_updated = True
                self.ad.md.delete_row('Staff Competency', db_sc)

        # Clear data widgets as entry deleted
        self.ent_prerequisite_date.delete(0, 9999)
        self.chc_achieved.deselect()
        self.ent_competency_date.delete(0, 9999)
        self.chc_completed.deselect()
        self.ent_notes.delete(0, 9999)
        self.chc_not_required.deselect()
        self.chc_required.deselect()

        # If in single record mode we close window to return to grid
        if self.single_record_mode:
            self.wnd_staff_competency.destroy()

    def handle_save_click(self):
        """Update the record for the Staff Name and Competency Name combination
           or insert a new one if it does not exist."""
        if self.single_record_mode:
            staff_name = self.inp_staff_name
            competency_name = self.inp_competency_name
        else:
            staff_name = self.cmb_staff_name.get()
            competency_name = self.cmb_competency_name.get()


        if staff_name and competency_name:
            prerequisite_date = parse_date(self.ent_prerequisite_date.get())
            achieved = self.chc_achieved.get()
            competency_date = parse_date(self.ent_competency_date.get())
            completed = self.chc_completed.get()
            notes = self.ent_notes.get()
            not_required = self.chc_not_required.get()
            required = self.chc_required.get()
            db_sc = self.ad.md.find_two('Staff Competency',
                                        staff_name, 'Staff Name',
                                        competency_name, 'Competency Name')

            # Validate dates
            if prerequisite_date:
                achieved = 1
            elif self.ent_prerequisite_date.get():
                input_warning(self.wnd_staff_competency,
                              f"Prerequisite Date {self.ent_prerequisite_date.get()} is not a valid date!")
                return

            if competency_date:
                completed = 1
            elif self.ent_competency_date.get():
                input_warning(self.wnd_staff_competency,
                              f"Competency Date {self.ent_competency_date.get()} is not a valid date!")
                return

            # If record found check for updates
            number_changes = 0
            if db_sc > -1:
                if (self.ad.md.get('Staff Competency', 'Prerequisite Date', db_sc) != prerequisite_date
                        or self.ad.md.get('Staff Competency', 'Achieved', db_sc) != achieved
                        or self.ad.md.get('Staff Competency', 'Competency Date', db_sc) != competency_date
                        or self.ad.md.get('Staff Competency', 'Completed', db_sc) != completed
                        or self.ad.md.get('Staff Competency', 'Notes', db_sc) != notes
                        or self.ad.md.get('Staff Competency', 'Not Required', db_sc) != not_required
                        or self.ad.md.get('Staff Competency', 'Required', db_sc) != required):
                    number_changes += 1
                    self.ad.master_updated = True
                    self.ad.md.update_row('Staff Competency', db_sc, {'Prerequisite Date': prerequisite_date,
                                                                      'Achieved': achieved,
                                                                      'Competency Date': competency_date,
                                                                      'Completed': completed,
                                                                      'Notes': notes,
                                                                      'Not Required': not_required,
                                                                      'Required': required})
            # Insert new record
            else:
                number_changes += 1
                self.ad.master_updated = True
                self.ad.md.add_row('Staff Competency', {'Staff Name': staff_name,
                                                        'Competency Name': competency_name,
                                                        'Prerequisite Date': prerequisite_date,
                                                        'Achieved': achieved,
                                                        'Competency Date': competency_date,
                                                        'Completed': completed,
                                                        'Notes': notes,
                                                        'Not Required': not_required,
                                                        'Required': required})

        # In single record mode close the window to return to grid
        if self.single_record_mode:
            self.wnd_staff_competency.destroy()
        else:
            CTkMessagebox(title="Information", message=f"{number_changes} changes saved", icon='info')
            if number_changes > 0:
                self.refresh_competency()

    def deselect_required(self):
        """Function to deselect the Required checkbox when Not Required is selected."""
        self.chc_required.deselect()

    def deselect_not_required(self):
        """Function to deselect the Not Required checkbox when Required is selected."""
        self.chc_not_required.deselect()
