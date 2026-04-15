"""This module defines the MasterData class which holds the master data
   and has methods to load, manipulate, access and save the data."""
import datetime
import logging
import os
import re
import shutil
import time
import warnings
from msilib import add_tables
from typing import Any, List, Union

import customtkinter as ctk
import pandas as pd
import portalocker
import xlsxwriter

logger = logging.getLogger(__name__)


class MasterData:
    def __init__(self,
                 master_excel_path: str,
                 retention: int,
                 wnd_parent: ctk.CTk | ctk.CTkToplevel | None = None,
                 password: str = '') -> None:

        logger.info(f"Creating MasterData for Excel {master_excel_path} with retention {retention}")
        self.tables = [
            'Service', 'Role', 'Staff', 'Competency',
            'Competency Service', 'Staff Role', 'Role Competency', 'Staff Competency']
        self.table_columns = {
            'Service': ['Service Name', 'Service Code'],
            'Role': ['Role Name', 'Role Code', 'RN', 'Display Order'],
            'Staff': ['Staff Name', 'Start Date', 'Practice Supervisor', 'Practice Assessor'],
            'Competency': ['Competency Name', 'Competency Name', 'Scope', 'Display Order', 'Expiry',
                           'Prerequisite', 'Nightshift', 'Bank'],
            'Competency Service': ['Competency Name', 'Service Code'],
            'Staff Role': ['Staff Name', 'Role Code', 'Service Code', 'Bank', 'Nightshift'],
            'Role Competency': ['Role Code', 'Competency Name', 'Service Code'],
            'Staff Competency': ['Staff Name', 'Competency Name', 'Prerequisite Date', 'Achieved',
                                 'Competency Date', 'Completed', 'Notes', 'Not Required', 'Required']}
        self.table_pkeys = {
            'Service': ['Service Code'],
            'Role': ['Role Code'],
            'Staff': ['Staff Name'],
            'Competency': ['Competency Name'],
            'Competency Service': ['Competency Name', 'Service Code'],
            'Staff Role': ['Staff Name', 'Role Code', 'Service Code'],
            'Role Competency': ['Role Code', 'Competency Name', 'Service Code'],
            'Staff Competency': ['Staff Name', 'Competency Name']}
        self.table_order = {
            'Service': ['Service Code'],
            'Role': ['Display Order'],
            'Staff': ['Staff Name'],
            'Competency': ['Display Order'],
            'Competency Service': ['Competency Name', 'Service Code'],
            'Staff Role': ['Staff Name', 'Role Code', 'Service Code'],
            'Role Competency': ['Service Code', 'Role Code', 'Competency Name'],
            'Staff Competency': ['Staff Name', 'Competency Name']}
        self.fkeys = [
            {'PTable': 'Service', 'FTable': 'Staff Role', 'FKey': 'Service Code'},
            {'PTable': 'Service', 'FTable': 'Role Competency', 'FKey': 'Service Code'},
            {'PTable': 'Service', 'FTable': 'Competency Service', 'FKey': 'Service Code'},
            {'PTable': 'Role', 'FTable': 'Staff Role', 'FKey': 'Role Code'},
            {'PTable': 'Role', 'FTable': 'Role Competency', 'FKey': 'Role Code'},
            {'PTable': 'Competency', 'FTable': 'Staff Competency', 'FKey': 'Competency Name'},
            {'PTable': 'Staff', 'FTable': 'Staff Role', 'FKey': 'Staff Name'},
            {'PTable': 'Staff', 'FTable': 'Staff Competency', 'FKey': 'Staff Name'},
            {'PTable': 'Competency', 'FTable': 'Competency Service', 'FKey': 'Competency Name'},
            {'PTable': 'Competency', 'FTable': 'Role Competency', 'FKey': 'Competency Name'}]

        self.user = os.getlogin()
        self.master_excel_path = master_excel_path
        self.retention = retention
        self._df = {}
        self._file_lock = None
        self.wnd_parent = wnd_parent
        self.password = password

    def __str__(self):
        """Function to generate string version of the master data as string of each of the data frames."""
        return str(f"Service\n{self._df['Service']}\n"
                   f"Role\n{self._df['Role']}"
                   f"Staff\n{self._df['Staff']}"
                   f"Competency\n{self._df['Competency']}"
                   f"Competency\n{self._df['Competency Service']}"
                   f"Staff Role\n{self._df['Staff Role']}"
                   f"Role Competency\n{self._df['Role Competency']}"
                   f"Staff Competency\n{self._df['Staff Competency']}")

    def _lock(self):
        """Lock the master data Excel file and create text file indicating the user who has locked it."""
        logger.info(f"Locking {self.master_excel_path}")
        if not self._file_lock:
            try:
                os.rename(self.master_excel_path, self.master_excel_path)
            except OSError as e:
                logger.warning(f"Can not lock master file {self.master_excel_path} error {e}")
                self._lock_error(self.master_excel_path, e)
            self._file_lock = open(self.master_excel_path, 'a')
            portalocker.lock(self._file_lock, portalocker.LOCK_EX)
            user_file_path = os.path.splitext(self.master_excel_path)[0] + '.txt'
            try:
                with open(user_file_path, 'w') as f:
                    f.write(self.user)
            except IOError as e:
                logger.warning(f"Failed to write user file {user_file_path} error {e}")

    def _unlock(self):
        """Unlock the master data Excel file."""
        logger.info(f"Unlocking {self.master_excel_path}")
        if self._file_lock:
            portalocker.unlock(self._file_lock)
            self._file_lock.close()
            self._file_lock = None
            user_file_path = os.path.splitext(self.master_excel_path)[0] + '.txt'
            if os.path.exists(user_file_path):
                os.remove(user_file_path)

    def _pkey_check(self, table: str) -> None:
        """Check a dataframe for duplicate primary keys."""
        df_dup = self._df[table][self._df[table].duplicated(
                     subset=self.table_pkeys[table],
                     keep=False)].sort_values(self.table_pkeys[table])
        if len(df_dup) > 0:
            self.data_error(f"{table} table contains duplicates\n{df_dup}")

    def _fkey_check(self, p_table: str, f_table: str, fkey: Union[list[str], str]) -> None:
        """Check that the foreign keys in a dataframe exist in the dataframe of primary keys."""
        df_missing = self._df[f_table].loc[~self._df[f_table][fkey].isin(self._df[p_table][fkey])].sort_values(fkey)
        if len(df_missing) > 0:
            self.data_error(f"{fkey} foreign key in {f_table} table not in {p_table} table\n{df_missing}")

    def sort_table(self, table: str) -> None:
        """Sort table into predefined order."""
        self._df[table].sort_values(self.table_order[table], inplace=True)
        self._df[table].reset_index(drop=True, inplace=True)

    def load(self, excel_path: str = None, readonly: bool = False) -> None:
        """Load the data from file. The path is optional for just this load keeping the master location the same.
           This allows an archive version of the master excel to be loaded to replace the current master."""
        if not excel_path:
            excel_path = self.master_excel_path

        # For read only set path to the copy
        if readonly:
            excel_path = os.path.splitext(self.master_excel_path)[0] + '_copy.xlsx'

        self._unlock()

        # Load sheets one at a time
        self._df = {}
        for table in self.tables:
            try:
                self._df[table] = pd.read_excel(excel_path, sheet_name=table, keep_default_na=False)
            except (IOError, ValueError) as e:
                # If Competency Service sheet is missing add it with all values set except for LEFT service code
                if table == 'Competency Service':
                    logger.info(f"Adding {table} table with all values set")
                    data = []
                    for competency_name in self._df['Competency']['Competency Name'].tolist():
                        if competency_name != 'LEFT':
                            for service_code in self._df['Service']['Service Code'].tolist():
                                data.append([competency_name, service_code])
                    self.add_table('Competency Service', self.table_columns['Competency Service'], data)
                else:
                    self._lock_error(excel_path, e)

        # Check columns exist on each sheet
        for table in self.table_columns:
            for column in self.table_columns[table]:
                if column not in self._df[table].columns:
                    msg = f"Table {table} column {column} not in Excel master file {excel_path}"
                    logger.warning(msg)
                    raise ValueError(msg)

        # For each table check primary keys and sort tables
        for table in self.tables:
            self._pkey_check(table)
            self.sort_table(table)

        # Check foreign keys
        for fkey in self.fkeys:
            self._fkey_check(fkey['PTable'], fkey['FTable'], fkey['FKey'])

        # Standardise date columns
        self._df['Staff']['Start Date'] = self._df['Staff']['Start Date'].apply(pandas_to_python_data)
        self._df['Staff Competency']['Prerequisite Date'] \
            = self._df['Staff Competency']['Prerequisite Date'].apply(pandas_to_python_data)
        self._df['Staff Competency']['Competency Date'] \
            = self._df['Staff Competency']['Competency Date'].apply(pandas_to_python_data)

        # If we are not in read only mode lock the master file
        if not readonly:
            self._lock()

    def _lock_error(self, excel_path: str, e: OSError):
        if not str(e).startswith('[Errno 13]') and not str(e).startswith('[WinError 32]'):
            raise IOError(e)
        try:
            user_file_path = os.path.splitext(self.master_excel_path)[0] + '.txt'
            with open(user_file_path, 'r') as f:
                current_user = f.readline()
        except IOError:
            logger.info(f"Master Excel {excel_path} in use e {e}")
            raise IOError(f"Master Excel in use")
        logger.info(f"Master Excel {excel_path} in use by {current_user}")
        raise IOError(f"Master Excel in use by {current_user}")

    def write(self):
        self._unlock()
        # Add date to current master file name and rename to create archive
        archive_excel_path = add_date_to_filename(self.master_excel_path)
        os.rename(self.master_excel_path, archive_excel_path)
        os.utime(archive_excel_path)

        # Define the sheet protect option
        protect_options = {
            'objects': False,
            'scenarios': False,
            'format_cells': True,
            'format_columns': True,
            'format_rows': True,
            'insert_columns': False,
            'insert_rows': False,
            'insert_hyperlinks': False,
            'delete_columns': False,
            'delete_rows': False,
            'select_locked_cells': True,
            'sort': False,
            'autofilter': True,
            'pivot_tables': False,
            'select_unlocked_cells': True,
        }
        # Create an Excel writer object
        with pd.ExcelWriter(self.master_excel_path, engine='xlsxwriter') as writer:
            wb = writer.book
            format_body = wb.add_format({'border': 1})
            for sheet_name, _df in self._df.items():
                _df.to_excel(writer, sheet_name=sheet_name, index=False, freeze_panes=(1, 0))
                ws = writer.sheets[sheet_name]  # Pull worksheet object
                # Hide grid lines and add borders
                ws.hide_gridlines(2)
                ws.conditional_format(
                    xlsxwriter.utility.xl_range(0, 0, len(_df), len(_df.columns) - 1),
                    {'type': 'no_errors', 'format': format_body})
                # Auto fit columns
                for col, column in enumerate(_df):  # Loop through all columns
                    series = _df[column]
                    max_len = max((
                        series.astype(str).map(len).max(),  # Length of largest item
                        len(str(series.name)) + 3,  # Length of column name plus 3 for filter dropdown
                        5  # Minimum width
                    )) + 2  # Adding extra space
                    ws.set_column(col, col, max_len)  # Set column width

                # Add filter to columns
                ws.autofilter(0, 0, len(_df), len(_df.columns) - 1)
                ws.protect(self.password, protect_options)

        # Crete a copy of the new master file for read only processes
        excel_copy = os.path.splitext(self.master_excel_path)[0] + '_copy.xlsx'
        shutil.copyfile(self.master_excel_path, excel_copy)

        # Lock Master Excel file
        self._lock()

        # Remove aged out historic Master Excel files
        self._housekeeping()

    def _housekeeping(self):
        """Remove historic Master Excel files older than retention period."""
        excel_directory = os.path.dirname(self.master_excel_path)
        excel_file_name = os.path.basename(self.master_excel_path)

        file_list = os.listdir(excel_directory)
        pattern = excel_file_name[:-5] + r'_\d{6}(_\d{1,5})?\.xlsx'
        for file in file_list:
            if re.match(pattern, file):
                file_path = os.path.join(excel_directory, file)
                if os.stat(file_path).st_mtime < time.time() - 86400 * self.retention:
                    logger.info(f"Removing {file_path}")
                    try:
                        os.remove(file_path)
                    except OSError as e:
                        logger.warning(f"Failed remove archive Master Excel {file_path} error {e}")

    def add_table(self, table: str, columns: List[str], data: List[List]) -> None:
        """Add a table to the dataframe dictionary with specified columns."""
        self._df[table] = pd.DataFrame(data, columns=columns)

    def update_row(self, table: str, index: int, update_row: dict) -> None:
        """Update the row with the specified index in the specified table with the values in the supplied dictionary.
           Values in the dictionary not in the table will be ignored. The table is not sorted incase the user is
           updating multiple rows and sorting will change the index."""
        for key, value in update_row.items():
            if key in self._df[table]:
                self._df[table].at[index, key] = value
        self._df[table].at[index, 'User'] = self.user
        self._df[table].at[index, 'Change Date'] = datetime.datetime.now()

    def add_row(self, table: str, new_row: dict) -> None:
        """Add a row to a table and set the audit columns. The table is resorted after the addition."""
        self._df[table].loc[len(self._df[table])] = new_row | {'User': self.user,
                                                               'Change Date': datetime.datetime.now()}
        self.sort_table(table)

    def get(self, table: str, column: str, index: int) -> Any:
        """Return the value of a colum in a table at an index."""
        return self._df[table].at[index, column]

    def get_list(self, table: str, column: str) -> List[Any]:
        """Return a column of a table as a list."""
        return self._df[table][column].tolist()

    def count(self, table: str, column: str, value: Any) -> int:
        """Count the occurrences of a value in a dataframe column."""
        try:
            return self._df[table][column].value_counts()[value]
        except KeyError:
            return 0

    def count_two(self, table: str, column1: str, value1: Any, column2: str, value2: Any) -> int:
        """Count the occurrences of a pair of value in a dataframe column."""
        try:
            return len(self._df[table][(self._df[table][column1] == value1) & (self._df[table][column2] == value2)])
        except KeyError:
            return 0

    def len(self, table: str) -> int:
        """Return the length of a table."""
        return len(self._df[table])

    def replace(self, table: str, column: str, old_value: Any, new_value: Any) -> None:
        """Replace all occurrences of a value with a new value in a column of a table."""
        mask = self._df[table][column] == old_value
        self._df[table].loc[mask, column] = new_value

    def delete_row(self, table: str, index: int) -> None:
        """Delete a row from a table with supplied index."""
        self._df[table].drop(index, inplace=True)
        self._df[table].reset_index(drop=True, inplace=True)

    def delete_value(self, table: str, column: str, value: Any) -> None:
        """Delete rows in a table where the specified colum has the supplied value."""
        self._df[table].drop(
            self._df[table][self._df[table][column] == value].index, inplace=True)
        self._df[table].reset_index(drop=True, inplace=True)

    def index(self, table: str, column: str, value: Any) -> int:
        """Find a value in a colum of a dataframe and return its index.
           If the value is not found it wil raise an IndexError exception."""
        return int(self._df[table][self._df[table][column] == value].index[0])

    def find_next(self, table: str, value: Any, column: str) -> int:
        """Return a dataframe index for the first occurrence of a value in a column greater
           than the supplied value. If the value is greater than the last value then
           the length of the table is returned."""
        try:
            return int(self._df[table][self._df[table][column] > value].index[0])
        except IndexError:
            return len(self._df[table])
        
    def find_one(self, table: str, value: Any, column: str, start: int = 0) -> int:
        """Return a dataframe index for the first occurrence of a value in a column.
           An index of -1 indicates that the value was not found."""
        warnings.filterwarnings(action='ignore', category=UserWarning, message=r"Boolean Series.*")
        idx = self._df[table][start:][self._df[table][column] == value].index
        if len(idx) > 0:
            return int(idx[0])
        return -1

    def find_two(self, table: str, value1: Any, column1: str, value2: Any, column2: str) -> int:
        """Return a dataframe index for the first occurrence of a pair of values in a
           pair of columns. An index of -1 indicates that the values were not found."""
        idx1 = self._df[table][self._df[table][column1] == value1].index
        idx2 = self._df[table][self._df[table][column2] == value2].index
        idx = idx1.intersection(idx2)
        try:
            return int(idx[0])
        except IndexError:
            return -1

    def find_three(self,
                   table: str,
                   value1: Any, column1: str,
                   value2: Any, column2: str,
                   value3: Any, column3: str) -> int:
        """Return a dataframe index for the first occurrence of a set of three values in a
           set of three columns. An index of -1 indicates that the values were not found."""
        idx1 = self._df[table][self._df[table][column1] == value1].index
        idx2 = self._df[table][self._df[table][column2] == value2].index
        idx3 = self._df[table][self._df[table][column3] == value3].index
        idx = idx1.intersection(idx2.intersection(idx3))
        try:
            return int(idx[0])
        except IndexError:
            return -1

    def data_error(self, error_text: str) -> None:
        """Function to display data errors in a window."""
        # This uses a CustomTinker window, if the UI changed this is the only routine that would have to be changed
        logger.warning(error_text)
        wnd_error = ctk.CTkToplevel()
        wnd_error.grab_set()
        wnd_error.title("Data Error Warning")
        txt_error = ctk.CTkTextbox(wnd_error, font=('Lucida Console', 14), width=700, wrap='none')
        txt_error.pack(fill='both', expand=True)
        txt_error.insert('0.0', error_text)
        txt_error.configure(state='disabled')

        # Set parent window cursor to wait (busy circle) then wait for this window to exit
        if self.wnd_parent:
            self.wnd_parent.config(cursor="watch")
            self.wnd_parent.wait_window(wnd_error)
            self.wnd_parent.config(cursor="")


def add_date_to_filename(path_name: str, file_ext: str = 'xlsx') -> str:
    """Function to set file path to a file that does not exist by adding
       date and file number to a supplied name and extension."""
    # Strip file extension from file name
    if path_name.endswith('.' + file_ext):
        path_name = path_name[:-len(file_ext) - 1]

    # Add date then if that exists add a file number until the file does not exist
    full_file_name = f"{path_name}_{datetime.date.today():%y%m%d}.{file_ext}"
    file_num = 0
    while os.path.exists(full_file_name):
        file_num = file_num + 1
        full_file_name = re.sub(r'(_\d{1,5})?\.' + file_ext, f'_{str(file_num)}.{file_ext}', full_file_name)

    return full_file_name


def pandas_to_python_data(pandas_datetime: Union[None, datetime.date, float, int]) -> Union[str, datetime.date]:
    """Function to convert a pandas date to a python datetime.date."""
    if not pandas_datetime:
        return ''
    if isinstance(pandas_datetime, datetime.datetime):
        return pandas_datetime.date()
    try:
        return datetime.datetime.fromtimestamp(pandas_datetime / 1E9).date()
    except TypeError:
        return ''
