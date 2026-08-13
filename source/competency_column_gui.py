import logging
from typing import Any

import customtkinter as ctk
import tkinter as tk
import pandas as pd

from appdata import AppData
from competency_diff_gui import CompetencyDiff
from competency_differences import CompetencyDifferences
from read_competency_report import read_competency_report
from window import child_window, input_warning, set_disabled_entry, date_to_string, parse_date

logger = logging.getLogger(__name__)


class CompetencyColumn(object):
    """Window to allow user to specify columns to use in competency report."""
    def __init__(self, ad: AppData, wnd_col: ctk.CTkToplevel, report_path: str) -> None:
        logger.info("Creating Competency Column Selection window")
        
        self.ad = ad
        self.wnd_col = wnd_col
        self.first_sample = 0
        self.num_sample = 4

        # Read competency report spreadsheet into a dataframe
        logger.info(f"Reading competency report: {report_path}")
        try:
            self.rep_df: pd.DataFrame = pd.read_excel(report_path, keep_default_na=False)
        except IOError as e:
            logger.error(f"Failed to open {report_path}: {e}")
            return

        # Limit sample to number of records read
        if self.num_sample > len(self.rep_df):
            self.num_sample = len(self.rep_df)

        def check_date(date_str: str) -> bool:
            """Checks if a date string is valid."""
            date = parse_date(date_str)
            if date:
                return True
            return False

        # Generate list of columns that contain dates and strings
        self.date_column: list[str] = []
        self.non_date_column: list[str] = []
        for column in self.rep_df.columns:
            if self.rep_df[column].dtypes == 'datetime64[ns]':
                self.date_column.append(column)
            elif self.rep_df[column].dtypes == 'object':
                if len(self.rep_df[self.rep_df[column].map(check_date)]) == len(self.rep_df):
                    self.date_column.append(column)
                else:
                    self.non_date_column.append(column)

        # Blank parameter column names if they do not exist
        if ad.args.first_name_column not in self.non_date_column:
            ad.args.first_name_column = ''
        if ad.args.surname_column not in self.non_date_column:
            ad.args.surname_column = ''
        if ad.args.comp_staff_column not in self.non_date_column:
            ad.args.comp_staff_column = ''
        if ad.args.comp_column not in self.non_date_column:
            ad.args.comp_column = ''
        if ad.args.comp_date_column not in self.date_column:
            ad.args.comp_date_column = ''

        wnd_col.title("Competency Column Selection")

        self.frm_col = ctk.CTkFrame(wnd_col)
        self.frm_col.pack(padx=6, fill='x', expand=False)

        # Sample data heading labels
        row: int = 0
        self.lbl_sample: list[ctk.CTkLabel] = []
        for i in range(self.num_sample):
            self.lbl_sample.append(ctk.CTkLabel(self.frm_col, text=f"Row {i+1}"))
            self.lbl_sample[i].grid(row=row, column=2+i, pady=6, padx=10, sticky='w')

        # Staff Name Column
        row += 1
        self.lbl_staff_name = ctk.CTkLabel(self.frm_col, text="Staff Name Column")
        self.lbl_staff_name.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_staff_name = ctk.CTkComboBox(self.frm_col, state='readonly',
                                              values=list(self.non_date_column),
                                              command=self.refresh_staff_name)
        self.cmb_staff_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        self.cmb_staff_name.set(ad.args.comp_staff_column)

        self.ent_staff_name: list[ctk.CTkEntry] = []
        for i in range(self.num_sample):
            self.ent_staff_name.append(ctk.CTkEntry(self.frm_col, state='disabled'))
            self.ent_staff_name[i].grid(row=row, column=2+i, pady=6, padx=10, sticky='w')

        # First Name Column
        row += 1
        self.lbl_first_name = ctk.CTkLabel(self.frm_col, text="First Name Column")
        self.lbl_first_name.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_first_name = ctk.CTkComboBox(self.frm_col, state='readonly',
                                              values=list(self.non_date_column),
                                              command=self.clear_staff_name)
        self.cmb_first_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        self.cmb_first_name.set(ad.args.first_name_column)

        self.ent_first_name: list[ctk.CTkEntry] = []
        for i in range(self.num_sample):
            self.ent_first_name.append(ctk.CTkEntry(self.frm_col, state='disabled'))
            self.ent_first_name[i].grid(row=row, column=2+i, pady=6, padx=10, sticky='w')

        # Surname Column
        row += 1
        self.lbl_surname = ctk.CTkLabel(self.frm_col, text="Surname Column")
        self.lbl_surname.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_surname = ctk.CTkComboBox(self.frm_col, state='readonly',
                                           values=list(self.non_date_column),
                                           command=self.clear_staff_name)
        self.cmb_surname.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        self.cmb_surname.set(ad.args.surname_column)

        self.ent_surname: list[ctk.CTkEntry] = []
        for i in range(self.num_sample):
            self.ent_surname.append(ctk.CTkEntry(self.frm_col, state='disabled'))
            self.ent_surname[i].grid(row=row, column=2+i, pady=6, padx=10, sticky='w')

        # Competency Column
        row += 1
        self.lbl_competency = ctk.CTkLabel(self.frm_col, text="Competency Column")
        self.lbl_competency.grid(row=row, column=0, pady=6, padx=10, sticky='e')

        self.cmb_competency = ctk.CTkComboBox(self.frm_col, state='readonly',
                                              values=list(self.non_date_column),
                                              command=self.set_sample_values)
        self.cmb_competency.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        self.cmb_competency.set(ad.args.comp_column)

        self.ent_competency: list[ctk.CTkEntry] = []
        for i in range(self.num_sample):
            self.ent_competency.append(ctk.CTkEntry(self.frm_col, state='disabled'))
            self.ent_competency[i].grid(row=row, column=2+i, pady=6, padx=10, sticky='w')

        # Competency Date Column
        row += 1
        self.lbl_date = ctk.CTkLabel(self.frm_col, text="Competency Date Column")
        self.lbl_date.grid(row=row, column=0, pady=6, padx=10, sticky='e')

        self.cmb_date = ctk.CTkComboBox(self.frm_col, state='readonly',
                                        values=list(self.date_column),
                                        command=self.set_sample_values)
        self.cmb_date.grid(row=row, column=1, pady=6, padx=10, sticky='w')
        self.cmb_date.set(ad.args.comp_date_column)

        self.ent_date: list[ctk.CTkEntry] = []
        for i in range(self.num_sample):
            self.ent_date.append(ctk.CTkEntry(self.frm_col, state='disabled'))
            self.ent_date[i].grid(row=row, column=2+i, pady=6, padx=10, sticky='w')

        # Create button frame
        self.frm_btn = ctk.CTkFrame(self.wnd_col)
        self.frm_btn.pack(fill='x', expand=False)

        self.btn_update = ctk.CTkButton(self.frm_btn, text="Read Report", command=self.read_report)
        self.btn_update.grid(row=0, column=0, pady=6, padx=10)

        self.btn_update = ctk.CTkButton(self.frm_btn, text="Previous Records", command=self.previous_records)
        self.btn_update.grid(row=0, column=1, pady=6, padx=10)

        self.btn_update = ctk.CTkButton(self.frm_btn, text="Next Records", command=self.next_records)
        self.btn_update.grid(row=0, column=2, pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(self.frm_btn, text="Exit", command=self.wnd_col.destroy)
        self.btn_exit.grid(row=0, column=3, pady=6, padx=10)

        # Initialise the sample data
        self.set_sample_values()

        # Check there is a date column available, do not close window as the user can explor what columns were loaded
        if len(self.date_column) == 0:
            input_warning(self.wnd_col, 'No date column in spreadsheet')

    def set_sample_values(self, event: Any = None) -> None:
        """Set the sample values based on the selected column names."""
        logger.debug(f"Called with event {event}")
        staff_name = self.cmb_staff_name.get()
        first_name = self.cmb_first_name.get()
        surname = self.cmb_surname.get()
        competency = self.cmb_competency.get()
        date = self.cmb_date.get()
        for i in range(self.num_sample):
            if staff_name:
                set_disabled_entry(self.ent_staff_name[i], self.rep_df.iloc[i+self.first_sample][staff_name])
            else:
                set_disabled_entry(self.ent_staff_name[i], '')

            if first_name:
                set_disabled_entry(self.ent_first_name[i], self.rep_df.iloc[i+self.first_sample][first_name])
            else:
                set_disabled_entry(self.ent_first_name[i], '')

            if surname:
                set_disabled_entry(self.ent_surname[i], self.rep_df.iloc[i+self.first_sample][surname])
            else:
                set_disabled_entry(self.ent_surname[i], '')

            if competency:
                set_disabled_entry(self.ent_competency[i], self.rep_df.iloc[i+self.first_sample][competency])
            else:
                set_disabled_entry(self.ent_competency[i], '')

            if date:
                if self.rep_df[date].dtypes == 'datetime64[ns]':
                    set_disabled_entry(self.ent_date[i], date_to_string(self.rep_df.iloc[i+self.first_sample][date]))
                else:
                    set_disabled_entry(self.ent_date[i], self.rep_df.iloc[i + self.first_sample][date])
            else:
                set_disabled_entry(self.ent_date[i], '')

    def next_records(self) -> None:
        """Move forward through sample records. This will wrap back to the start of the data if the end is reached."""
        if self.first_sample + self.num_sample * 2 <= len(self.rep_df):
            self.first_sample += self.num_sample
        else:
            self.first_sample = 0

        for i in range(self.num_sample):
            self.lbl_sample[i].configure(text=f'Row {i+self.first_sample+1}')
        self.set_sample_values()

    def previous_records(self) -> None:
        """Move backwards through sample records. This will wrap around to the end if the start is reached"""
        if self.first_sample >= self.num_sample:
            self.first_sample -= self.num_sample
        else:
            self.first_sample = len(self.rep_df) - self.num_sample

        for i in range(self.num_sample):
            self.lbl_sample[i].configure(text=f'Row {i+self.first_sample+1}')
        self.set_sample_values()

    def refresh_staff_name(self, event: Any) -> None:
        """Clear first name and surname columns names when staff name column is set, then refresh the sample data."""
        logger.debug(f"Called with event {event}")
        self.cmb_first_name.set('')
        self.cmb_surname.set('')
        self.set_sample_values()

    def clear_staff_name(self, event: Any) -> None:
        """Clear staff name when first name or surname columns names are set, then refresh the sample data."""
        logger.debug(f"Called with event {event}")
        self.cmb_staff_name.set('')
        self.set_sample_values()

    def read_report(self) -> None:
        """Read and validate the competency column names then call the procedures
           to analyse the differences and give the user the ability to address them."""
        self.ad.args.comp_staff_column = self.cmb_staff_name.get()
        self.ad.args.first_name_column = self.cmb_first_name.get()
        self.ad.args.surname_column = self.cmb_surname.get()
        self.ad.args.comp_column = self.cmb_competency.get()
        self.ad.args.date_column = self.cmb_date.get()
        if not self.ad.args.comp_staff_column and not (self.ad.args.first_name_column and self.ad.args.surname_column):
            input_warning(self.wnd_col, "Staff Name Column or First Name and Surname Columns must be set")
            return
        if not self.ad.args.comp_column:
            input_warning(self.wnd_col, "Competency Column must be set")
            return
        if not self.ad.args.date_column:
            input_warning(self.wnd_col, "Competency Date Column must be set")
            return

        diff: CompetencyDifferences = CompetencyDifferences()
        read_competency_report(self.ad, self.rep_df, diff)
        if diff:
            child_window(CompetencyDiff, self.ad, self.wnd_col, diff)

        self.wnd_col.destroy()
