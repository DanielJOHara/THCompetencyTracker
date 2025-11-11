"""This module contains the business logic for the role competency management.

"""
import logging
from source.appdata import AppData

logger = logging.getLogger(__name__)

class RoleCompetencyLogic:
    """Encapsulates the business logic for role competency management."""

    def __init__(self, ad: AppData):
        """Initializes the RoleCompetencyLogic.

        Args:
            ad: The application's data object.
        """
        self.ad = ad

    def get_competency_list(self, staff_type: str) -> list:
        """Gets a list of competencies for a given staff type.

        Args:
            staff_type: The staff type to filter by.

        Returns:
            A list of competency database indices.
        """
        db_c_list = []
        for db_c in range(self.ad.md.len('Competency')):
            if self.ad.md.get('Competency', 'Scope', db_c) in [staff_type, 'BOTH']:
                db_c_list.append(db_c)
        return db_c_list

    def get_role_list(self, staff_type: str) -> list:
        """Gets a list of roles for a given staff type.

        Args:
            staff_type: The staff type to filter by.

        Returns:
            A list of role database indices.
        """
        db_r_list = []
        for db_r in range(self.ad.md.len('Role')):
            rn = self.ad.md.get('Role', 'RN', db_r)
            if rn and staff_type == 'RN' or not rn and staff_type != 'RN':
                db_r_list.append(db_r)
        return db_r_list

    def save_role_competencies(self, service_code: str, db_c_list: list, db_r_list: list, chc_rc: list) -> int:
        """Saves the role competency grid.

        Args:
            service_code: The service code.
            db_c_list: A list of competency database indices.
            db_r_list: A list of role database indices.
            chc_rc: A 2D list of checkbox widgets.

        Returns:
            The number of changes made.
        """
        number_changes = 0
        for c, db_c in enumerate(db_c_list):
            competency_name = self.ad.md.get('Competency', 'Competency Name', db_c)
            for r, db_r in enumerate(db_r_list):
                role_code = self.ad.md.get('Role', 'Role Code', db_r)
                chc_status = chc_rc[c][r].get()
                db_rc = self.ad.md.find_three('Role Competency',
                                              service_code, 'Service Code',
                                              role_code, 'Role Code',
                                              competency_name, 'Competency Name')

                # If there is a record for Role Competency combination and its checkbox is unchecked then delete it
                if db_rc > -1:
                    if not chc_status:
                        number_changes += 1
                        self.ad.master_updated = True
                        self.ad.md.delete_row('Role Competency', db_rc)

                # If there is no record for Role Competency combination and its checkbox is checked add one
                else:
                    if chc_status:
                        number_changes += 1
                        self.ad.master_updated = True
                        self.ad.md.add_row('Role Competency', {'Service Code': service_code,
                                                               'Role Code': role_code,
                                                               'Competency Name': competency_name})
        return number_changes

    def reset_role_competencies(self, service_code: str, db_c_list: list, db_r_list: list, chc_rc: list) -> None:
        """Resets the role competency grid to the values in the database.

        Args:
            service_code: The service code.
            db_c_list: A list of competency database indices.
            db_r_list: A list of role database indices.
            chc_rc: A 2D list of checkbox widgets.
        """
        for c, db_c in enumerate(db_c_list):
            competency_name = self.ad.md.get('Competency', 'Competency Name', db_c)
            for r, db_r in enumerate(db_r_list):
                role_code = self.ad.md.get('Role', 'Role Code', db_r)
                chc_status = chc_rc[c][r].get()
                db_rc = self.ad.md.find_three('Role Competency',
                                              service_code, 'Service Code',
                                              role_code, 'Role Code',
                                              competency_name, 'Competency Name')

                # If there is a record for Role Competency combination and its checkbox is not checked then check it
                if db_rc > -1:
                    if not chc_status:
                        chc_rc[c][r].select()

                # If there is no record for Role Competency combination and its checkbox is checked then uncheck it
                else:
                    if chc_status:
                        chc_rc[c][r].deselect()
