"""This module contains the business logic for the role service management."""
import logging
from source.appdata import AppData
from source.master_data import MasterDataError

logger = logging.getLogger(__name__)


class RoleServiceLogic:
    """Encapsulates the business logic for role service management."""

    def __init__(self, ad: AppData):
        """Initializes the RoleServiceLogic.

        Args:
            ad: The application's data object.
        """
        self.ad = ad

    def save_role_services(self, value_rs: list) -> int:
        """Saves the role service grid.

        Args:
            value_rs: A 2D list of flag values.

        Returns:
            The number of changes made.
        """
        number_changes = 0
        for db_r in range(self.ad.md.len('Role')):
            role_code = self.ad.md.get('Role', 'Role Code', db_r)
            for db_s in range(self.ad.md.len('Service')):
                service_code = self.ad.md.get('Service', 'Service Code', db_s)
                db_rs = self.ad.md.find_two('Role Service',
                                            role_code, 'Role Code',
                                            service_code, 'Service Code')

                # If there is a record for Role Service combination and its checkbox is unchecked then delete it
                if db_rs > -1:
                    if not value_rs[db_r][db_s]:
                        number_changes += 1
                        self.ad.master_updated = True
                        self.ad.md.delete_row('Role Service', db_rs)

                # If there is no record for Role Service combination and its checkbox is checked add one
                else:
                    if value_rs[db_r][db_s]:
                        number_changes += 1
                        self.ad.master_updated = True
                        self.ad.md.add_row('Role Service', {'Role Code': role_code,
                                                            'Service Code': service_code})

        return number_changes

    def save_role_service(self, role_code: str, value_s: list) -> int:
        """Saves the role services for an individual role.

        Args:
            role_code: The role code.
            value_s: A list of flag values for the role's services.

        Returns:
            The number of changes made.
        """
        number_changes = 0
        for db_s in range(self.ad.md.len('Service')):
            service_code = self.ad.md.get('Service', 'Service Code', db_s)
            db_rs = self.ad.md.find_two('Role Service',
                                        role_code, 'Role Code',
                                        service_code, 'Service Code')

            # If there is a record for Role Service combination and its checkbox is unchecked then delete it
            if db_rs > -1:
                if not value_s[db_s]:
                    number_changes += 1
                    self.ad.master_updated = True
                    self.ad.md.delete_row('Role Service', db_rs)

            # If there is no record for Role Service combination and its checkbox is checked add one
            else:
                if value_s[db_s]:
                    number_changes += 1
                    self.ad.master_updated = True
                    self.ad.md.add_row('Role Service', {'Role Code': role_code,
                                                        'Service Code': service_code})

        return number_changes
