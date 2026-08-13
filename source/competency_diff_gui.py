import logging
from datetime import date

import customtkinter as ctk
import tkinter as tk
from CTkMessagebox import CTkMessagebox

from appdata import AppData
from competency_diff_report import competency_diff_report
from competency_differences import CompetencyDifferences, Competency
from competency_gui import CompetencyAdd
from master_data import MasterDataError
from staff_competency_gui import StaffCompetencyUpdate
from staff_gui import StaffAdd
from window import child_window, show_master_data_error

logger = logging.getLogger(__name__)


class CompetencyDiff(object):
    """Window to allow user to process differences between the loaded competency report and
       the master data defined in a data object. The user can export a report of the differences
       and can add missing or update altered records in the master data."""
    def __init__(self, ad: AppData, wnd_comp_load: ctk.CTkToplevel, diff: CompetencyDifferences) -> None:
        logger.info("Creating Competency data update window")

        self.wnd_comp_load = wnd_comp_load
        self.ad = ad
        self.diff = diff

        # Add title top window
        wnd_comp_load.title("Competency Differance Review")

        self.frm_counts = ctk.CTkFrame(wnd_comp_load)
        self.frm_counts.pack(padx=6, fill='x', expand=False)

        # Missing Competency Names
        row: int = 0
        self.lbl_missing_comp = ctk.CTkLabel(self.frm_counts, text=f"{len(diff.missing_competency)}")
        self.lbl_missing_comp.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.lbl_missing_comp_txt = ctk.CTkLabel(self.frm_counts, text="Missing Competency Names")
        self.lbl_missing_comp_txt.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        if len(diff.missing_competency) > 0:
            self.btn_missing_comp = ctk.CTkButton(self.frm_counts, text="Add Competency",
                                                  command=self.handle_missing_comp_click)
            self.btn_missing_comp.grid(row=row, column=3, pady=6, padx=10)

        # Missing Staff Names
        row += 1
        self.lbl_missing_staff = ctk.CTkLabel(self.frm_counts, text=f"{len(diff.missing_staff)}")
        self.lbl_missing_staff.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.lbl_missing_staff_txt = ctk.CTkLabel(self.frm_counts, text="Missing Staff Names")
        self.lbl_missing_staff_txt.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        if len(diff.missing_staff) > 0:
            self.btn_missing_staff = ctk.CTkButton(self.frm_counts, text="Add Staff",
                                                   command=self.handle_missing_staff_click)
            self.btn_missing_staff.grid(row=row, column=3, pady=6, padx=10)

        # Missing Staff Competencies
        row += 1
        self.lbl_missing_staff_comp = ctk.CTkLabel(self.frm_counts, text=f"{len(diff.missing_staff_comp)}")
        self.lbl_missing_staff_comp.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.lbl_missing_staff_comp_txt = ctk.CTkLabel(self.frm_counts, text="Missing Staff Competencies")
        self.lbl_missing_staff_comp_txt.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        if len(diff.missing_staff) > 0:
            self.btn_missing_staff_comp = ctk.CTkButton(self.frm_counts, text="Add Staff Competency",
                                                        command=self.handle_missing_staff_comp_click)
            self.btn_missing_staff_comp.grid(row=row, column=3, pady=6, padx=10)

        # Competency Date Changes
        row += 1
        self.lbl_date_change = ctk.CTkLabel(self.frm_counts, text=f"{len(diff.staff_comp_date)}")
        self.lbl_date_change.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.lbl_date_change_txt = ctk.CTkLabel(self.frm_counts, text="Competency Date Changes")
        self.lbl_date_change_txt.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        if len(diff.staff_comp_date) > 0:
            self.btn_date_change = ctk.CTkButton(self.frm_counts, text="Change Dates",
                                                  command=self.handle_date_change_click)
            self.btn_date_change.grid(row=row, column=3, pady=6, padx=10)

        # Extra Competency Names", Staff Names and Staff Competencies.
        # There is no process to update the system that generated the repot.
        row += 1
        self.lbl_extra_comp = ctk.CTkLabel(self.frm_counts, text=f"{len(diff.extra_competency)}")
        self.lbl_extra_comp.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.lbl_extra_comp_txt = ctk.CTkLabel(self.frm_counts, text="Extra Competency Names")
        self.lbl_extra_comp_txt.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_extra_staff = ctk.CTkLabel(self.frm_counts, text=f"{len(diff.extra_staff)}")
        self.lbl_extra_staff.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.lbl_extra_staff_txt = ctk.CTkLabel(self.frm_counts, text="Extra Staff Names")
        self.lbl_extra_staff_txt.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_extra_staff_comp = ctk.CTkLabel(self.frm_counts, text=f"{len(diff.extra_staff_comp)}")
        self.lbl_extra_staff_comp.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.lbl_extra_staff_comp_txt = ctk.CTkLabel(self.frm_counts, text="Extra Staff Competencies")
        self.lbl_extra_staff_comp_txt.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        # Create button frame
        self.frm_btn = ctk.CTkFrame(self.wnd_comp_load)
        self.frm_btn.pack(fill='x', expand=False)

        self.btn_update = ctk.CTkButton(self.frm_btn, text="Export Differences", command=self.handle_export_click)
        self.btn_update.grid(row=0, column=0, pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(self.frm_btn, text="Exit", command=self.wnd_comp_load.destroy)
        self.btn_exit.grid(row=0, column=1, pady=6, padx=10)

    def handle_export_click(self) -> None:
        """Prompt user for the location to write competency difference
           report Excel file and call function to write it."""
        report_path = tk.filedialog.asksaveasfilename(
            initialdir=self.ad.args.report_directory,
            initialfile=f"Competencies Export {date.today():%Y-%m-%d}",
            title="Select Competency Export Excel File",
            filetype=(('xlsx files', '*.xlsx'),)).replace('/', '\\')

        logger.info(f"User selected to export competency difference report Excel: {report_path}")
        if report_path:
            if report_path[-5:] != '.xlsx':
                report_path += '.xlsx'
            competency_diff_report(report_path, self.diff)

    def handle_missing_comp_click(self) -> None:
        """Function to create child windows to input missing competencies in the master data."""
        logger.info(f"User clicked to load {len(self.diff.missing_competency)} missing competencies")
        for competency_name in self.diff.missing_competency:
            if self.ad.md.find_one('Competency', competency_name, 'Competency Name') == -1:
                child_window(CompetencyAdd, self.ad, self.wnd_comp_load, competency_name)
        self.diff.missing_competency = [competency_name for competency_name in self.diff.missing_competency
                                        if self.ad.md.find_one('Competency', competency_name, 'Competency Name') == -1]
        self.lbl_missing_comp.configure(text=f"{len(self.diff.missing_competency)}")
        if len(self.diff.missing_competency) == 0:
            self.lbl_missing_comp.destroy()

    def handle_missing_staff_click(self) -> None:
        """Function to create child windows to input missing staff in the master data."""
        logger.info(f"User clicked to load {len(self.diff.missing_staff)} missing staff")
        staff_name_list = self.diff.missing_staff.copy()
        for staff_name in staff_name_list:
            if self.ad.md.find_one('Staff', staff_name, 'Staff Name') == -1:
                child_window(StaffAdd, self.ad, self.wnd_comp_load, staff_name)
        self.diff.missing_staff = [staff_name for staff_name in self.diff.missing_staff
                                   if self.ad.md.find_one('Staff', staff_name, 'Staff Name') == -1]
        self.lbl_missing_staff.configure(text=f"{len(self.diff.missing_staff)}")
        if len(self.diff.missing_staff) == 0:
            self.btn_missing_staff.destroy()

    def handle_missing_staff_comp_click(self) -> None:
        """Function to call a function to update the master data with the missing competencies."""
        logger.info(f"User clicked to load {len(self.diff.missing_staff_comp)} missing staff competencies")
        self.load_competencies(self.diff.missing_staff_comp)

        # Remove entries from the missing competencies list where they now exist
        self.diff.missing_staff_comp = [competency for competency in self.diff.missing_staff_comp
                                        if self.ad.md.find_two('Staff Competency',
                                                               competency.staff_name, 'Staff Name',
                                                               competency.competency_name, 'Competency Name') == -1]
        self.lbl_missing_staff_comp.configure(text=f"{len(self.diff.missing_staff_comp)}")
        if len(self.diff.missing_staff_comp) == 0:
            self.btn_missing_staff_comp.destroy()

    def handle_date_change_click(self) -> None:
        """Function to call a the function below function to update the master data with the competency date changes.
           Then remove records from the difference data object where the dates now match."""
        logger.info(f"User clicked change {len(self.diff.staff_comp_date)} staff competency dates")
        self.load_competencies(self.diff.staff_comp_date)

        # Produce a list of the indexes of the data difference records where the dates now match
        date_match_list: list[int] = []
        for i, competency in enumerate(self.diff.staff_comp_date):
            db_sc = self.ad.md.find_two('Staff Competency',
                                        competency.staff_name, 'Staff Name',
                                        competency.competency_name, 'Competency Name')
            if db_sc > -1:
                competency_date = self.ad.md.get('Staff Competency', 'Competency Date', db_sc)
                if competency_date == competency.competency_date:
                    date_match_list.append(i)

        # Remove the identified records in revers order to not invalidate the indexes before they are processed
        for i in reversed(date_match_list):
            self.diff.staff_comp_date.pop(i)

        # Update the count label and remove the button if there are no remaining date differences
        self.lbl_date_change.configure(text=f"{len(self.diff.staff_comp_date)}")
        if len(self.diff.staff_comp_date) == 0:
            self.btn_date_change.destroy()

    def load_competencies(self, competency_changes: list[Competency]) -> None:
        """Function to update the master data with the supplied competency which can be missing
           competencies or date changes."""
        msg = CTkMessagebox(title="Option",
                            message="Accept all changes or review one at a time",
                            option_1='Accept All',
                            option_2='Review')

        # When accepting all changes check if the record exist and update it or add a new record
        if msg.get() == 'Accept All':
            logger.info("User opted to accepted all changes")
            for competency in competency_changes:
                db_sc = self.ad.md.find_two('Staff Competency',
                                            competency.staff_name, 'Staff Name',
                                            competency.competency_name, 'Competency Name')
                if db_sc > -1:
                    try:
                        self.ad.master_updated = True
                        self.ad.md.update_row('Staff Competency',
                                              db_sc,
                                              {'Competency Date': competency.competency_date,
                                               'Completed': 1,
                                               'Notes': "Date updated from competency report"})
                    except MasterDataError as e:
                        show_master_data_error(str(e), self.wnd_comp_load)
                        return
                else:
                    try:
                        self.ad.master_updated = True
                        self.ad.md.add_row('Staff Competency',
                                           {'Staff Name': competency.staff_name,
                                            'Competency Name': competency.competency_name,
                                            'Competency Date': competency.competency_date,
                                            'Completed': 1,
                                            'Notes': "Added from competency report"})
                    except MasterDataError as e:
                        show_master_data_error(str(e), self.wnd_comp_load)
                        return

        # When reviewing record call the staff competency update window for a record at a time. This window
        # will add or update the record as necessary. After each 10 records check the user wants to continue.
        elif msg.get() == 'Review':
            logger.info("User opted to review changes one at a time")
            for i, competency in enumerate(competency_changes):
                if i % 10 == 9:
                    msg = CTkMessagebox(title="Option",
                                        message=f"{i+1} of {len(competency_changes)} records processed",
                                        option_1='Continue', option_2='Stop')
                    if msg.get() != 'Continue':
                        break
                child_window(StaffCompetencyUpdate, self.ad, self.wnd_comp_load,
                             competency.staff_name, competency.competency_name, competency.competency_date)
