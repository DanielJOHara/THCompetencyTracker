"""This module contains the business logic for the competency service management."""
import logging
from source.appdata import AppData
from source.master_data import MasterDataError
from source.window import show_master_data_error

logger = logging.getLogger(__name__)


class CompetencyServiceLogic:
    """Encapsulates the business logic for competency service management."""

    def __init__(self, ad: AppData):
        """Initializes the CompetencyServiceLogic.

        Args:
            ad: The application's data object.
        """
        self.ad = ad

    def save_all_competency_service(self, chc_cs: list) -> int:
        """Saves the competency service grid.

        Args:
            chc_cs: A 2D list of checkbox widgets.

        Returns:
            The number of changes made.
        """
        number_changes = 0
        try:
            for db_c in range(self.ad.md.len('Competency')):
                competency_name = self.ad.md.get('Competency', 'Competency Name', db_c)
                for db_s in range(self.ad.md.len('Service')):
                    service_code = self.ad.md.get('Service', 'Service Code', db_s)
                    chc_status = chc_cs[db_c][db_s].get()
                    db_cs = self.ad.md.find_two('Competency Service',
                                                competency_name, 'Competency Name',
                                                service_code, 'Service Code')

                    # If there is a record for Competency Service combination and its checkbox is unchecked then delete it
                    if db_cs > -1:
                        if not chc_status:
                            number_changes += 1
                            self.ad.master_updated = True
                            self.ad.md.delete_row('Competency Service', db_cs)

                    # If there is no record for Competency Service combination and its checkbox is checked add one
                    else:
                        if chc_status:
                            number_changes += 1
                            self.ad.master_updated = True
                            self.ad.md.add_row('Competency Service', {'Competency Name': competency_name,
                                                                    'Service Code': service_code})
        except MasterDataError as e:
            show_master_data_error(str(e), self.ad.wnd_root)

        return number_changes

    def reset_competency_service(self, chc_cs: list) -> None:
        """Resets the competency service grid to the values in the database.

        Args:
            chc_cs: A 2D list of checkbox widgets.
        """
        for db_c in range(self.ad.md.len('Competency')):
            competency_name = self.ad.md.get('Competency', 'Competency Name', db_c)
            for db_s in range(self.ad.md.len('Service')):
                service_code = self.ad.md.get('Service', 'Service Code', db_s)
                chc_status = chc_cs[db_c][db_s].get()
                db_cs = self.ad.md.find_two('Competency Service',
                                            competency_name, 'Competency Name',
                                            service_code, 'Service Code')

                # If there is a record for Competency Service combination and its checkbox is not checked then check it
                if db_cs > -1:
                    if not chc_status:
                        chc_cs[db_c][db_s].select()

                # If there is no record for Competency Service combination and its checkbox is checked then uncheck it
                elif chc_status:
                    chc_cs[db_c][db_s].deselect()

    def save_competency_service(self, competency_name: str, chc_services: list) -> int:
        """Saves the competency services for an individual competency.

        Args:
            competency_name: The competency name.
            chc_services: A list of checkbox widgets for the competency's services.

        Returns:
            The number of changes made.
        """
        number_changes = 0
        try:
            for db_s in range(self.ad.md.len('Service')):
                service_code = self.ad.md.get('Service', 'Service Code', db_s)
                chc_status = chc_services[db_s].get()
                db_cs = self.ad.md.find_two('Competency Service',
                                            competency_name, 'Competency Name',
                                            service_code, 'Service Code')

                # If there is a record for Competency Service combination and its checkbox is unchecked then delete it
                if db_cs > -1:
                    if not chc_status:
                        number_changes += 1
                        self.ad.master_updated = True
                        self.ad.md.delete_row('Competency Service', db_cs)

                # If there is no record for Competency Service combination and its checkbox is checked add one
                else:
                    if chc_status:
                        number_changes += 1
                        self.ad.master_updated = True
                        self.ad.md.add_row('Competency Service', {'Competency Name': competency_name,
                                                                'Service Code': service_code})
        except MasterDataError as e:
            show_master_data_error(str(e), self.ad.wnd_root)

        return number_changes
