"""This module contains the business logic for the role service management."""
import logging
from source.appdata import AppData
from source.master_data import MasterDataError
from source.window import show_master_data_error

logger = logging.getLogger(__name__)


class RoleServiceLogic:
    """Encapsulates the business logic for role service management."""

    def __init__(self, ad: AppData):
        """Initializes the RoleServiceLogic.

        Args:
            ad: The application's data object.
        """
        self.ad = ad

    def save_all_role_service(self, chc_cs: list) -> int:
        """Saves the role service grid.

        Args:
            chc_cs: A 2D list of checkbox widgets.

        Returns:
            The number of changes made.
        """
        number_changes = 0
        try:
            for db_r in range(self.ad.md.len('Role')):
                role_code = self.ad.md.get('Role', 'Role Code', db_r)
                for db_s in range(self.ad.md.len('Service')):
                    service_code = self.ad.md.get('Service', 'Service Code', db_s)
                    chc_status = chc_cs[db_r][db_s].get()
                    db_rs = self.ad.md.find_two('Role Service',
                                                role_code, 'Role Code',
                                                service_code, 'Service Code')

                    # If there is a record for Role Service combination and its checkbox is unchecked then delete it
                    if db_rs > -1:
                        if not chc_status:
                            number_changes += 1
                            self.ad.master_updated = True
                            self.ad.md.delete_row('Role Service', db_rs)

                    # If there is no record for Role Service combination and its checkbox is checked add one
                    else:
                        if chc_status:
                            number_changes += 1
                            self.ad.master_updated = True
                            self.ad.md.add_row('Role Service', {'Role Code': role_code,
                                                                'Service Code': service_code})
        except MasterDataError as e:
            show_master_data_error(str(e), self.ad.wnd_root)

        return number_changes

    def reset_role_service(self, chc_cs: list) -> None:
        """Resets the role service grid to the values in the database.

        Args:
            chc_cs: A 2D list of checkbox widgets.
        """
        for db_r in range(self.ad.md.len('Role')):
            role_code = self.ad.md.get('Role', 'Role Code', db_r)
            for db_s in range(self.ad.md.len('Service')):
                service_code = self.ad.md.get('Service', 'Service Code', db_s)
                chc_status = chc_cs[db_r][db_s].get()
                db_rs = self.ad.md.find_two('Role Service',
                                            role_code, 'Role Code',
                                            service_code, 'Service Code')

                # If there is a record for Role Service combination and its checkbox is not checked then check it
                if db_rs > -1:
                    if not chc_status:
                        chc_cs[db_r][db_s].select()

                # If there is no record for Role Service combination and its checkbox is checked then uncheck it
                elif chc_status:
                    chc_cs[db_r][db_s].deselect()

    def save_role_service(self, role_code: str, chc_services: list) -> int:
        """Saves the role services for an individual role.

        Args:
            role_code: The role code.
            chc_services: A list of checkbox widgets for the role's services.

        Returns:
            The number of changes made.
        """
        number_changes = 0
        try:
            for db_s in range(self.ad.md.len('Service')):
                service_code = self.ad.md.get('Service', 'Service Code', db_s)
                chc_status = chc_services[db_s].get()
                db_rs = self.ad.md.find_two('Role Service',
                                            role_code, 'Role Code',
                                            service_code, 'Service Code')

                # If there is a record for Role Service combination and its checkbox is unchecked then delete it
                if db_rs > -1:
                    if not chc_status:
                        number_changes += 1
                        self.ad.master_updated = True
                        self.ad.md.delete_row('Role Service', db_rs)

                # If there is no record for Role Service combination and its checkbox is checked add one
                else:
                    if chc_status:
                        number_changes += 1
                        self.ad.master_updated = True
                        self.ad.md.add_row('Role Service', {'Role Code': role_code,
                                                            'Service Code': service_code})
        except MasterDataError as e:
            show_master_data_error(str(e), self.ad.wnd_root)

        return number_changes
