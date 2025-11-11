"""This module contains the business logic for the staff role management.

"""
import logging
import re
from source.appdata import AppData

logger = logging.getLogger(__name__)


class StaffRoleLogic:
    """Encapsulates the business logic for staff role management."""

    def __init__(self, ad: AppData):
        """Initializes the StaffRoleLogic.

        Args:
            ad: The application's data object.
        """
        self.ad = ad

    def save_staff_roles(self, staff_name: str, role_list: list,
                         bank_list: list, nightshift_list: list) -> tuple[bool, int, str]:
        """Saves all changes made to the staff roles.

        Args:
            staff_name: The name of the staff member.
            role_list: A list the role values.
            bank_list: A list of bank values.
            nightshift_list: A list of nightshift values.

        Returns:
            A tuple containing an input valid flag, number of changes and a message.
        """
        if not staff_name:
            return False, 0, "No staff member selected."

        number_changes = 0
        for db_sc, service_code in enumerate(self.ad.md.get_list('Service', 'Service Code')):
            role_code = role_list[db_sc]
            db_sr = self.ad.md.find_two('Staff Role', service_code, 'Service Code', staff_name, 'Staff Name')
            if not role_code:
                if db_sr > -1:
                    self.ad.md.delete_row('Staff Role', db_sr)
                    number_changes += 1
                    self.ad.master_updated = True
                continue

            bank = bank_list[db_sc]
            nightshift = nightshift_list[db_sc]
            if db_sr < 0:
                number_changes += 1
                self.ad.master_updated = True
                self.ad.md.add_row('Staff Role', {'Service Code': service_code,
                                                  'Staff Name': staff_name,
                                                  'Role Code': role_code,
                                                  'Bank': bank,
                                                  'Nightshift': nightshift})
            else:
                if (self.ad.md.get('Staff Role', 'Role Code', db_sr) != role_code
                        or self.ad.md.get('Staff Role', 'Bank', db_sr) != bank
                        or self.ad.md.get('Staff Role', 'Nightshift', db_sr) != nightshift):
                    number_changes += 1
                    self.ad.master_updated = True
                    self.ad.md.update_row('Staff Role', db_sr, {'Role Code': role_code,
                                                                'Bank': bank,
                                                                'Nightshift': nightshift})

        return True, number_changes, f"{number_changes} changes saved"

    def delete_staff_roles(self, staff_name: str) -> None:
        """Deletes all roles for a staff member.

        Args:
            staff_name: The name of the staff member.
        """
        self.ad.md.delete_value('Staff Role', 'Staff Name', staff_name)

    def filter_staff_names(self, name_filter: str) -> list:
        """Filters the staff names based on a filter string.

        Args:
            name_filter: The filter string.

        Returns:
            A list of filtered staff names.
        """
        if name_filter:
            # Remove every thing except letters and spaces from filter string
            name_filter = re.sub(r'[^a-zA-Z -]', '', name_filter).strip()
            filter_name_lst = []
            for staff_name in self.ad.md.get_list('Staff', 'Staff Name'):
                if re.search(name_filter, staff_name, re.IGNORECASE):
                    filter_name_lst.append(staff_name)
            return filter_name_lst
        else:
            return self.ad.md.get_list('Staff', 'Staff Name')
