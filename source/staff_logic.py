"""This module contains the business logic for managing staff."""
import logging
import re
from source.appdata import AppData
from source.window import parse_date

logger = logging.getLogger(__name__)


class StaffLogic(object):
    """Business logic for managing staff."""
    def __init__(self, ad: AppData):
        """Initialise the StaffLogic class."""
        self.ad = ad

    def save_staff(self, staff_values: list, db_s_list: list) -> tuple[int, str]:
        """Read all values in table and update the table object if any values
           have changed."""
        number_changes = 0
        for s, db_s in enumerate(db_s_list):
            staff_name = re.sub(' +', ' ', staff_values[s]['Staff Name'].strip())
            old_staff_name = self.ad.md.get('Staff', 'Staff Name', db_s)
            if old_staff_name != staff_name:
                logger.info(f"Changing Staff Name from >{old_staff_name}< to >{staff_name}<")
                # Check name change does not conflict with an existing record
                if self.ad.md.count('Staff', 'Staff Name', staff_name) > 0:
                    return 0, f"Can't change Staff Name {old_staff_name} to {staff_name} as it already exists"
                else:
                    # Propagate Staff Name changes to foreign keys in other tables
                    self.ad.master_updated = True
                    self.ad.md.replace('Staff Role', 'Staff Name', old_staff_name, staff_name)
                    self.ad.md.replace('Staff Competency', 'Staff Name', old_staff_name, staff_name)

            start_date = parse_date(staff_values[s]['Start Date'])
            if (old_staff_name != staff_name
                    or self.ad.md.get('Staff', 'Start Date', db_s) != start_date
                    or self.ad.md.get('Staff', 'Practice Supervisor', db_s) != staff_values[s]['Practice Supervisor']
                    or self.ad.md.get('Staff', 'Practice Assessor', db_s) != staff_values[s]['Practice Assessor']):
                number_changes += 1
                logger.info(f"Updating Staff Name {old_staff_name}")
                self.ad.master_updated = True
                self.ad.md.update_row('Staff', db_s, {'Staff Name': staff_name,
                                                      'Start Date': start_date,
                                                      'Practice Supervisor': staff_values[s]['Practice Supervisor'],
                                                      'Practice Assessor': staff_values[s]['Practice Assessor']})
        
        if number_changes > 0:
            self.ad.md.sort_table('Staff')

        return number_changes, f"{number_changes} changes saved"

    def add_staff(self, staff_name: str, start_date: str,
                  practice_supervisor: int, practice_assessor: int) -> tuple[bool, str]:
        """Add a new staff member."""
        staff_name = re.sub(' +', ' ', staff_name.strip())
        
        if not staff_name:
            return False, "Staff Name field must be set!"
        elif start_date and not parse_date(start_date):
            return False, f"Start Date {start_date} is not a valid date!"

        # Find Staff Name to update or add a new one
        try:
            self.ad.md.index('Staff', 'Staff Name', staff_name)
        except IndexError:
            self.ad.master_updated = True
            self.ad.md.add_row('Staff', {'Staff Name': staff_name,
                                         'Start Date': parse_date(start_date),
                                         'Practice Supervisor': practice_supervisor,
                                         'Practice Assessor': practice_assessor})
            return True, f"Added {staff_name}"
        else:
            return False, f"Staff Name {staff_name} is already defined!"

    def delete_staff(self, staff_name: str) -> tuple[bool, bool, str]:
        """Delete a staff member and their dependent records."""
        if not staff_name:
            return False, False, "No staff member selected."

        # Warn that dependent rows will be deleted
        sr_cnt = self.ad.md.count('Staff Role', 'Staff Name', staff_name)
        sc_cnt = self.ad.md.count('Staff Competency', 'Staff Name', staff_name)
        if sr_cnt or sc_cnt:
            warn_text = f"{staff_name} is used {sr_cnt} times in Staff Role and {sc_cnt} times in Staff Competency"
            return False, True, warn_text

        self.delete_staff_with_dependents(staff_name)
        
        return True, False, f"{staff_name} deleted."

    def delete_staff_with_dependents(self, staff_name: str):
        """Delete a staff member and their dependent records."""
        db_s = self.ad.md.index('Staff', 'Staff Name', staff_name)

        # Delete row and dependent rows, note deletes not audited
        self.ad.master_updated = True
        self.ad.md.delete_row('Staff', db_s)

        # Delete entries for Staff Name in Staff Role dataframe
        self.ad.md.delete_value('Staff Role', 'Staff Name', staff_name)

        # Delete entries for Staff Name in Staff Competency table
        self.ad.md.delete_value('Staff Competency', 'Staff Name', staff_name)

    def apply_filters(self, name_filter: str, no_role_filter: int,
                      service_filter: list, role_filter: list) -> list[int]:
        """Apply filters to the staff list."""
        if name_filter:
            name_filter = re.sub(r"[^a-zA-Z -']", '', name_filter).strip()

        db_s_list = []
        for db_s, staff_name in enumerate(self.ad.md.get_list("Staff", 'Staff Name')):
            # If staff name doesn't pass filter stop testing
            if name_filter and not re.search(name_filter, staff_name, re.I):
                continue

            # For staff with no roles only add them if role staff are to be included
            if self.ad.md.count('Staff Role', 'Staff Name', staff_name) == 0:
                if no_role_filter:
                    db_s_list.append(db_s)
                continue

            # Check each role
            db_sr = self.ad.md.find_one('Staff Role', staff_name, 'Staff Name')
            while db_sr > -1:
                role_code = self.ad.md.get('Staff Role', 'Role Code', db_sr)
                service_code = self.ad.md.get('Staff Role', 'Service Code', db_sr)
                if service_code in service_filter and role_code in role_filter:
                    db_s_list.append(db_s)
                    break
                db_sr = self.ad.md.find_one('Staff Role', staff_name, 'Staff Name', start=db_sr+1)

        return db_s_list
