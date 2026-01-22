"""This module displays the windows to select Competency tracking processes.
   This is a main selection window and child windows to pass options to the processes."""
import logging
import os
import re

import customtkinter as ctk
import datetime
import tkinter as tk

from source.appdata import AppData
from source.window import child_window, input_warning
from source.staff_competency_gui import StaffCompetencyUpdate
from source.staff_competency_grid_gui import StaffCompetencyGrid
from source.staff_competency_grid_export import competency_grid_export
from source.competency_report import competency_report
from source.staff_report import staff_report
from source.staff_document import staff_document

logger = logging.getLogger(__name__)


class CompetencyTracking(object):
    """Window to offer user list of competency tracking options."""

    def __init__(self, ad: AppData, wnd_track: ctk.CTkToplevel) -> None:
        logger.info("Creating Competency Tracking window")

        self.ad = ad
        self.wnd_track = wnd_track

        wnd_track.title("Competency Tracking")

        self.frm_button = ctk.CTkFrame(wnd_track)
        self.frm_button.pack(pady=20, padx=60, fill='both', expand=True)

        # Do not display competency update button in read only mode
        if not self.ad.args.readonly:
            self.btn_review = ctk.CTkButton(self.frm_button, text="Competency Grid",
                                            command=lambda: child_window(StaffCompetencyGridSelect, ad, wnd_track))
            self.btn_review.pack(pady=12, padx=20)

            self.btn_input = ctk.CTkButton(self.frm_button, text="Competency Input",
                                           command=lambda: child_window(StaffCompetencyUpdate, ad, wnd_track))
            self.btn_input.pack(pady=12, padx=20)

        self.btn_grid = ctk.CTkButton(self.frm_button, text="Grid Export",
                                      command=lambda: child_window(ReportSelect, ad, wnd_track, 'GRID'))
        self.btn_grid.pack(pady=12, padx=20)

        self.btn_competency = ctk.CTkButton(self.frm_button, text="Competency Report",
                                            command=lambda: child_window(ReportSelect, ad, wnd_track, 'COMPETENCY'))
        self.btn_competency.pack(pady=12, padx=20)

        self.btn_staff = ctk.CTkButton(self.frm_button, text="Staff Report",
                                       command=lambda: child_window(ReportSelect, ad, wnd_track, 'STAFF'))

        self.btn_staff.pack(pady=12, padx=20)

        self.btn_staff_doc = ctk.CTkButton(self.frm_button, text="Staff Documents",
                                           command=lambda: child_window(StaffDocumentSelect, ad, wnd_track))
        self.btn_staff_doc.pack(pady=12, padx=20)

        # When in read only mode this is the base window so display application name and version
        if self.ad.args.readonly:
            self.lbl_about = ctk.CTkLabel(self.wnd_track, text=f"{ad.app_name} {ad.app_version}")
            self.lbl_about.pack(pady=0, padx=20, anchor='e')

        self.wnd_track.protocol('WM_DELETE_WINDOW', self.on_closing)

    def on_closing(self) -> None:
        self.wnd_track.destroy()
        if self.ad.args.readonly:
            self.ad.wnd_root.destroy()


class StaffCompetencyGridSelect(object):
    """Window for the user to enter the Service Code and Staff Type for which
       to generate the staff competency grid."""
    def __init__(self, ad: AppData, wnd_cg_select: ctk.CTkToplevel) -> None:
        logger.info("Creating Staff Competency Grid Selection window")

        self.wnd_cg_select = wnd_cg_select
        self.ad = ad

        # Add title top window
        wnd_cg_select.title("Staff Competency Grid Selection")

        self.frm_attribute = ctk.CTkFrame(wnd_cg_select)
        self.frm_attribute.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_service_code = ctk.CTkLabel(self.frm_attribute, text="Font Size")
        self.lbl_service_code.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_font_size = ctk.CTkEntry(self.frm_attribute)
        self.ent_font_size.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        self.ent_font_size.insert(0, '10')

        row += 1
        self.lbl_service_code = ctk.CTkLabel(self.frm_attribute, text="Service Code")
        self.lbl_service_code.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_service_code = ctk.CTkComboBox(self.frm_attribute, state='readonly',
                                                values=ad.md.get_list('Service', 'Service Code'),
                                                command=self.call_review)
        self.cmb_service_code.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_staff_type = ctk.CTkLabel(self.frm_attribute, text="Staff Type")
        self.lbl_staff_type.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_staff_type = ctk.CTkComboBox(self.frm_attribute, state='readonly',
                                              values=['RN', 'HCA'], command=self.call_review)
        self.cmb_staff_type.grid(row=row, column=1, pady=6, padx=10, sticky='w')

    # noinspection PyUnusedLocal
    def call_review(self, event) -> None:
        """Function to review inputs and call staff competency grid window if required."""
        if not self.ent_font_size.get():
            font_size = 10
        elif not self.ent_font_size.get().isdigit():
            input_warning(self.wnd_cg_select, "Font Size must be integer or blank!")
            return
        else:
            font_size = int(self.ent_font_size.get())

        service_code = self.cmb_service_code.get()
        staff_type = self.cmb_staff_type.get()
        if service_code and staff_type:
            # Call routine to generate grid, waiting for it to close then close this window
            child_window(StaffCompetencyGrid, self.ad, self.wnd_cg_select, service_code, staff_type, font_size)
            self.wnd_cg_select.destroy()


class ReportSelect(object):
    """Window for the user to enter the Service Codes and Staff Types for which
       to generate the grid export, staff report or competency report."""
    def __init__(self, ad: AppData, wnd_report_select: ctk.CTkToplevel, report_type: str) -> None:

        self.ad = ad
        self.wnd_report_select = wnd_report_select

        if report_type == 'GRID':
            self.report_title = "Staff Competency Grid"
            self.report_procedure = competency_grid_export
        elif report_type == 'COMPETENCY':
            self.report_title = "Competency Report"
            self.report_procedure = competency_report
        elif report_type == 'STAFF':
            self.report_title = "Staff Report"
            self.report_procedure = staff_report
        else:
            logger.error(f"ReportSelect called with invalid report type: {report_type}")
            input_warning(self.wnd_report_select, "Failed to Generate Report")
            return

        logger.info(f"Creating {self.report_title} Selection Window")

        # Add title top window
        wnd_report_select.title(f"{self.report_title} Select")

        self.frm_attribute = ctk.CTkFrame(wnd_report_select)
        self.frm_attribute.pack(fill='both', expand=True)

        # Generate list of check boxes for service codes in column 0
        row = 0
        self.lbl_service_code = ctk.CTkLabel(self.frm_attribute, text="Service Code")
        self.lbl_service_code.grid(row=row, column=0, pady=6, padx=10, sticky='w')

        self.chc_service_code_list = []
        for s, service_code in enumerate(self.ad.md.get_list('Service', 'Service Code')):
            row += 1
            self.chc_service_code_list.append(ctk.CTkCheckBox(self.frm_attribute, text=service_code))
            self.chc_service_code_list[s].grid(row=row, column=0, pady=6, padx=20, sticky='e')
            self.chc_service_code_list[s].bind("<Button-1>", command=self.set_default_file)

        # Generate check boxes for staff types in column 1
        row = 0
        self.lbl_staff_type = ctk.CTkLabel(self.frm_attribute, text="Staff Type")
        self.lbl_staff_type.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.chc_rn = ctk.CTkCheckBox(self.frm_attribute, text='RN')
        self.chc_rn.grid(row=row, column=1, pady=6, padx=20, sticky='e')
        self.chc_rn.bind("<Button-1>", command=self.set_default_file)

        row += 1
        self.chc_hca = ctk.CTkCheckBox(self.frm_attribute, text='HCA')
        self.chc_hca.grid(row=row, column=1, pady=6, padx=20, sticky='e')
        self.chc_hca.bind("<Button-1>", command=self.set_default_file)

        # Generate action buttons in column 2
        row = 0
        self.btn_generate = ctk.CTkButton(self.frm_attribute, text="Generate",
                                          command=self.generate_report)
        self.btn_generate.grid(row=row, column=2, pady=6, padx=10)

        # Create frame for file location
        self.frm_files = ctk.CTkFrame(wnd_report_select)
        self.frm_files.pack(fill='both', expand=True)

        row = 0
        self.btn_report_path = ctk.CTkButton(self.frm_files, text="Report File", command=self.file_select)
        self.btn_report_path.grid(row=row, column=0, pady=6, padx=10)
        self.lbl_report_path = ctk.CTkLabel(self.frm_files)
        self.lbl_report_path.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        # Set export file path to the default
        self.report_path = self.ad.args.report_directory + '//dummy.xlsx'
        self.set_default_file()

    def set_default_file(self, event: str = None) -> None:
        logger.debug(f"ReportSelect set_default_file called with event {event}")

        service_code_list, staff_type_list = self.set_report_lists()
        scope = ' '.join(service_code_list) + ' - ' + ' '.join(staff_type_list)

        report_directory = str(os.path.dirname(self.report_path))
        report_file = f'{self.report_title} {scope} {datetime.date.today():%Y-%m-%d}.xlsx'
        self.report_path = str(os.path.join(report_directory, report_file))
        self.lbl_report_path.configure(text=self.report_path)

    def set_report_lists(self) -> [list, list]:
        """Function to read check boxes for service codes and staff types and return selections in two lists."""
        
        # Set service code list from list of check boxs
        service_code_list = []
        for s, service_code in enumerate(self.ad.md.get_list('Service', 'Service Code')):
            if self.chc_service_code_list[s].get():
                service_code_list.append(service_code)

        # Set staff type list from RN and HCA check boxes
        staff_type_list = []
        if self.chc_rn.get():
            staff_type_list.append('RN')
        if self.chc_hca.get():
            staff_type_list.append('HCA')
        
        return service_code_list, staff_type_list

    def generate_report(self) -> None:
        # Get service code and staff type selections in two lists
        service_code_list, staff_type_list = self.set_report_lists()
        if len(service_code_list) < 1 and len(staff_type_list) < 1:
            input_warning(self.wnd_report_select, "Check required Service Codes and Staff Types")
            return
        if len(service_code_list) < 1:
            input_warning(self.wnd_report_select, "Check required Service Codes")
            return
        if len(staff_type_list) < 1:
            input_warning(self.wnd_report_select, "Check required Staff Types")
            return

        # Call external routine to generate the report
        self.report_procedure(self.ad, self.report_path, service_code_list, staff_type_list)

    def file_select(self) -> None:
        """Function to provide Excel report path to competency grid export generation."""
        # Prompt user for Excel file for report
        report_directory = str(os.path.dirname(self.report_path))
        report_file = str(os.path.basename(self.report_path))
        report_excel_path = tk.filedialog.asksaveasfilename(
            initialdir=report_directory,
            initialfile=report_file,
            title="Select Report Excel File",
            filetype=(('xlsx files', '*.xlsx'),)).replace('/', '\\')
        logger.info(f"User selected to generate report file: {report_excel_path}")

        if not report_excel_path:
            return

        # Add Excel file extension if it is missing
        if report_excel_path[-5:] != '.xlsx':
            report_excel_path += '.xlsx'

        self.report_path = report_excel_path
        self.lbl_report_path.configure(text=self.report_path)


class StaffDocumentSelect(object):
    def __init__(self, ad: AppData, wnd_sd_select: ctk.CTkToplevel) -> None:
        logger.info("Creating Staff Document Selection window")

        self.wnd_sd_select = wnd_sd_select
        self.ad = ad

        # Add title top window
        wnd_sd_select.title("Staff Document Select")

        # Create Staff Member attribute frame
        self.frm_attribute = ctk.CTkFrame(wnd_sd_select)
        # self.frm_attribute.pack(fill='both', side='left', expand=True)
        self.frm_attribute.grid(row=0, column=0, sticky='nsew')

        self.staff_list = []
        self.lbl_staff_list = []

        row = 0
        self.lbl_staff_name = ctk.CTkLabel(self.frm_attribute, text="Staff Name")
        self.lbl_staff_name.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_staff_name = ctk.CTkComboBox(self.frm_attribute, state='readonly',
                                              values=ad.md.get_list('Staff', 'Staff Name'))
        self.cmb_staff_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.add = ctk.CTkButton(self.frm_attribute, text="Add", command=self.add_staff)
        self.add.grid(row=row, column=1, pady=12, padx=20)

        row += 1
        self.remove = ctk.CTkButton(self.frm_attribute, text="Remove", command=self.remove_staff)
        self.remove.grid(row=row, column=1, pady=12, padx=20)

        row += 1
        self.generate = ctk.CTkButton(self.frm_attribute, text="Generate", command=self.generate_documents)
        self.generate.grid(row=row, column=1, pady=12, padx=20)

        # Create lookup frame for filters
        self.frm_lookup = ctk.CTkFrame(wnd_sd_select)
        # self.frm_lookup.pack(fill='both', side='left', expand=True)
        self.frm_lookup.grid(row=0, column=1, sticky='nsew')

        row = 1
        self.lbl_name_filter = ctk.CTkLabel(self.frm_lookup, text="Name Filter")
        self.lbl_name_filter.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_name_filter = ctk.CTkEntry(self.frm_lookup)
        self.ent_name_filter.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        self.ent_name_filter.bind("<Return>", command=self.apply_filters)
        self.ent_name_filter.bind("<Leave>", command=self.apply_filters)

        row += 1
        self.lbl_rn_filter = ctk.CTkLabel(self.frm_lookup, text="RN Filter")
        self.lbl_rn_filter.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_rn_filter = ctk.CTkComboBox(self.frm_lookup, state='readonly',
                                             values=['', 'RN', 'HCA'], command=self.apply_filters)
        self.cmb_rn_filter.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_role_filter = ctk.CTkLabel(self.frm_lookup, text="Role Filter")
        self.lbl_role_filter.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_role_filter = ctk.CTkComboBox(self.frm_lookup, state='readonly',
                                               values=[''] + ad.md.get_list('Role', 'Role Code'),
                                               command=self.apply_filters)
        self.cmb_role_filter.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_service_filter = ctk.CTkLabel(self.frm_lookup, text="Service Filter")
        self.lbl_service_filter.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_service_filter = ctk.CTkComboBox(self.frm_lookup, state='readonly',
                                                  values=[''] + ad.md.get_list('Service', 'Service Code'),
                                                  command=self.apply_filters)
        self.cmb_service_filter.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        # Create frame for staff list
        self.frm_staff_list = ctk.CTkFrame(wnd_sd_select)
        self.frm_staff_list.grid(row=0, column=2, sticky='nsew')

        self.lbl_staff_list_title = ctk.CTkLabel(self.frm_staff_list, text="Staff List",
                                                 height=30, width=150, corner_radius=6, fg_color='#00B0F0')
        self.lbl_staff_list_title.pack(pady=6, padx=10, anchor='w')

        # Create frame for file locations
        self.frm_files = ctk.CTkFrame(wnd_sd_select)
        self.frm_files.grid(row=1, column=0, columnspan=3, sticky='nsew')

        # Set template file to the default
        self.template_path = os.path.join(self.ad.args.master_excel_directory, 'Staff Template.docx')

        row = 0
        self.btn_template = ctk.CTkButton(self.frm_files, text="Template", command=self.select_template)
        self.btn_template.grid(row=row, column=0, pady=6, padx=10)
        self.lbl_template = ctk.CTkLabel(self.frm_files, text=self.template_path)
        self.lbl_template.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        # Default document directory to a folder for today under a staff document sub directory
        self.document_directory = os.path.join(self.ad.args.report_directory,
                                               'Staff Documents', f'{datetime.date.today():%Y-%m-%d}')
        if not os.path.exists(self.document_directory):
            os.makedirs(self.document_directory)

        row += 1
        self.btn_document = ctk.CTkButton(self.frm_files, text="Documents", command=self.select_document_directory)
        self.btn_document.grid(row=row, column=0, pady=6, padx=10)
        self.lbl_document = ctk.CTkLabel(self.frm_files, text=self.document_directory)
        self.lbl_document.grid(row=row, column=1, pady=6, padx=10, sticky='w')

    def add_staff(self):
        staff_name = self.cmb_staff_name.get()
        if not staff_name:
            logger.info(f"Add button clicked with no staff name selected")
            return
        logger.info(f"Adding {staff_name} to Staff List")
        if staff_name not in self.staff_list:
            self.staff_list.append(staff_name)
        self.staff_list.sort()
        self.refresh_list()

    def remove_staff(self):
        staff_name = self.cmb_staff_name.get()
        logger.info(f"Removing {staff_name} from Staff List")
        if staff_name in self.staff_list:
            self.staff_list.remove(staff_name)
        self.refresh_list()

    def refresh_list(self):
        for s, staff_name in enumerate(self.staff_list):
            if s > len(self.lbl_staff_list) - 1:
                self.lbl_staff_list.append(ctk.CTkLabel(self.frm_staff_list, text=staff_name))
                self.lbl_staff_list[s].pack(pady=0, padx=10, anchor='w')
            else:
                self.lbl_staff_list[s].configure(text=staff_name)

        # Remove staff labels that are no longer used
        for i in range(len(self.lbl_staff_list) - len(self.staff_list)):
            self.lbl_staff_list[-1].destroy()
            self.lbl_staff_list.pop()

    def select_template(self):
        # Prompt user for Staff Document Template file to use
        new_template_path = tk.filedialog.askopenfilename(
            initialdir=self.ad.args.master_excel_directory,
            initialfile='Staff Template.docx',
            title="Select Staff Document Template File",
            filetype=(('xlsx files', '*.docx'),)).replace('/', '\\')
        logger.info(f"User selected to use Staff Document Template file: {new_template_path}")

        # If user selected template update
        if new_template_path:
            self.template_path = new_template_path
            self.lbl_template.configure(text=self.template_path)

        return

    def select_document_directory(self):
        # Prompt user for destination directory
        new_document_directory = tk.filedialog.askdirectory(
            initialdir=self.document_directory,
            title="Select Staff Document Directory").replace('/', '\\')
        logger.info(f"User selected to generate Staff Documents in: {new_document_directory}")

        # If user selects directory set
        if new_document_directory:
            self.document_directory = new_document_directory
            self.lbl_document.configure(text=self.document_directory)

        return

    def generate_documents(self):
        if len(self.staff_list) < 1:
            return

        staff_document(self.ad, self.staff_list, self.template_path, self.document_directory)

    def apply_filters(self, event: str = None):
        logger.debug(f"apply_filters called with event {event}")
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
            if len(filter_name_lst) == 1:
                self.cmb_staff_name.set(filter_name_lst[0])
            elif self.cmb_staff_name.get() not in filter_name_lst:
                self.cmb_staff_name.set('')
        else:
            self.cmb_staff_name.configure(values=self.ad.md.get_list('Staff', 'Staff Name'))
