"""This module contains the business logic for the competency service management."""
import logging
from source.appdata import AppData
from source.master_data import MasterDataError

logger = logging.getLogger(__name__)


class CompetencyServiceLogic:
    """Encapsulates the business logic for competency service management."""

    def __init__(self, ad: AppData):
        """Initializes the CompetencyServiceLogic.

        Args:
            ad: The application's data object.
        """
        self.ad = ad

    def save_competency_services(self, value_cs: list) -> int:
        """Saves the competency service grid.

        Args:
            value_cs: A 2D list of flag values.

        Returns:
            The number of changes made.
        """
        number_changes = 0
        for db_c in range(self.ad.md.len('Competency')):
            competency_name = self.ad.md.get('Competency', 'Competency Name', db_c)
            for db_s in range(self.ad.md.len('Service')):
                service_code = self.ad.md.get('Service', 'Service Code', db_s)
                db_cs = self.ad.md.find_two('Competency Service',
                                            competency_name, 'Competency Name',
                                            service_code, 'Service Code')

                # If there is a record for Competency Service combination
                # and its checkbox is unchecked then delete it
                if db_cs > -1:
                    if not value_cs[db_c][db_s]:
                        number_changes += 1
                        self.ad.master_updated = True
                        self.ad.md.delete_row('Competency Service', db_cs)

                # If there is no record for Competency Service combination and its checkbox is checked add one
                else:
                    if value_cs[db_c][db_s]:
                        number_changes += 1
                        self.ad.master_updated = True
                        self.ad.md.add_row('Competency Service', {'Competency Name': competency_name,
                                                                  'Service Code': service_code})

        return number_changes

    def save_competency_service(self, competency_name: str, value_s: list) -> int:
        """Saves the competency services for an individual competency.

        Args:
            competency_name: The competency name.
            value_s: A list of flag values for the competency's services.

        Returns:
            The number of changes made.
        """
        number_changes = 0
        for db_s in range(self.ad.md.len('Service')):
            service_code = self.ad.md.get('Service', 'Service Code', db_s)
            db_cs = self.ad.md.find_two('Competency Service',
                                        competency_name, 'Competency Name',
                                        service_code, 'Service Code')

            # If there is a record for Competency Service combination and its checkbox is unchecked then delete it
            if db_cs > -1:
                if not value_s[db_s]:
                    number_changes += 1
                    self.ad.master_updated = True
                    self.ad.md.delete_row('Competency Service', db_cs)

            # If there is no record for Competency Service combination and its checkbox is checked add one
            else:
                if value_s[db_s]:
                    number_changes += 1
                    self.ad.master_updated = True
                    self.ad.md.add_row('Competency Service', {'Competency Name': competency_name,
                                                              'Service Code': service_code})

        return number_changes
