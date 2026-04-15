"""This module contains the business logic for the competency management.

"""
import logging
from source.appdata import AppData

logger = logging.getLogger(__name__)


class CompetencyLogic:
    """Encapsulates the business logic for competency management."""

    def __init__(self, ad: AppData):
        """Initializes the CompetencyLogic.

        Args:
            ad: The application's data object.
        """
        self.ad = ad

    def save_competencies(self, competency_values: list) -> tuple[bool, int, str]:
        """Saves all changes made to the competencies.

        Args:
            competency_values: A list of values the competencies.

        Returns:
            A tuple containing the number of changes and a message.
        """
        # Validate integer attributes
        for db_c in range(self.ad.md.len('Competency')):
            if not competency_values[db_c]['Display Order'].isdigit():
                return False, 0, "Display Order field must be integer!"
            if competency_values[db_c]['Expiry'] and not competency_values[db_c]['Expiry'].isdigit():
                return False, 0, "Expiry field must be integer or blank!"

        # Check every value to see if it has changed
        number_changes = 0
        for db_c in range(self.ad.md.len('Competency')):
            # Propagate Competency Name changes to foreign keys in other tables
            new_competency_name = competency_values[db_c]['Competency Name']
            old_competency_name = self.ad.md.get('Competency', 'Competency Name', db_c)
            if self.ad.md.get('Competency', 'Competency Name', db_c) != new_competency_name:
                self.ad.master_updated = True
                self.ad.md.replace('Role Competency', 'Competency Name', old_competency_name, new_competency_name)
                self.ad.md.replace('Staff Competency', 'Competency Name', old_competency_name, new_competency_name)
                self.ad.md.replace('Competency Service', 'Competency Name', old_competency_name, new_competency_name)

            if competency_values[db_c]['Expiry']:
                new_expiry = int(competency_values[db_c]['Expiry'])
            else:
                new_expiry = ''
            new_display_order = int(competency_values[db_c]['Display Order'])
            new_scope = competency_values[db_c]['Scope']
            new_prerequisite = competency_values[db_c]['Prerequisite']
            new_nightshift = competency_values[db_c]['Nightshift']
            new_bank = competency_values[db_c]['Bank']
            if (old_competency_name != new_competency_name
                    or self.ad.md.get('Competency', 'Display Order', db_c) != new_display_order
                    or self.ad.md.get('Competency', 'Scope', db_c) != new_scope
                    or self.ad.md.get('Competency', 'Prerequisite', db_c) != new_prerequisite
                    or self.ad.md.get('Competency', 'Nightshift', db_c) != new_nightshift
                    or self.ad.md.get('Competency', 'Bank', db_c) != new_bank):
                number_changes += 1
                self.ad.master_updated = True
                self.ad.md.update_row('Competency', db_c,
                                      {'Competency Name': new_competency_name,
                                       'Display Order': new_display_order,
                                       'Scope': new_scope,
                                       'Expiry': new_expiry,
                                       'Prerequisite': new_prerequisite,
                                       'Nightshift': new_nightshift,
                                       'Bank': new_bank})

        if number_changes > 0:
            self.ad.md.sort_table('Competency')

        return True, number_changes, f"{number_changes} changes saved"

    def delete_competency(self, competency_name: str) -> tuple[bool, bool, str]:
        """Deletes a competency and its dependent records.

        Args:
            competency_name: The name of the competency to delete.

        Returns:
            A tuple containing a boolean indicating success and a message.
        """
        if not competency_name:
            return False, False, "No competency selected."

        # Warn that dependent rows will be deleted
        rc_cnt = self.ad.md.count('Role Competency', 'Competency Name', competency_name)
        sc_cnt = self.ad.md.count('Staff Competency', 'Competency Name', competency_name)
        cs_cnt = self.ad.md.count('Competency Service', 'Competency Name', competency_name)
        if rc_cnt or sc_cnt or cs_cnt:
            warn_text = (f"{competency_name} is used {rc_cnt} times in Role Competency,"
                         f" {sc_cnt} times in Staff Competency and {cs_cnt} times in Competency Service.")
            return False, True, warn_text

        self.delete_competency_with_dependents(competency_name)
        return True, False, f"{competency_name} deleted."

    def delete_competency_with_dependents(self, competency_name: str):
        """Deletes a competency and its dependent records.

        Args:
            competency_name: The name of the competency to delete.
        """
        db_c = self.ad.md.index('Competency', 'Competency Name', competency_name)

        # Delete row and dependent rows, note deletes not audited
        self.ad.master_updated = True
        self.ad.md.delete_row('Competency', db_c)

        # Delete entries for Competency Name in Role Competency table
        self.ad.md.delete_value('Role Competency', 'Competency Name', competency_name)

        # Delete entries for Competency Name in Staff Competency table
        self.ad.md.delete_value('Staff Competency', 'Competency Name', competency_name)

        # Delete entries for Competency Name in Competency Service table
        self.ad.md.delete_value('Competency Service', 'Competency Name', competency_name)

    def add_competency(self, competency_name: str,
                       scope: str,
                       display_order: str,
                       expiry: str,
                       prerequisite: int,
                       nightshift: int,
                       bank: int) -> tuple[bool, str]:
        """Adds a new competency.

        Args:
            competency_name: The name of the new competency.
            scope: The scope of the new competency.
            display_order: The display order of the new competency.
            expiry: The expiry of the new competency.
            prerequisite: Whether the new competency is a prerequisite.
            nightshift: Whether the new competency is a nightshift competency.
            bank: Whether the new competency is a bank competency.

        Returns:
            A tuple containing a boolean indicating success and a message.
        """
        if not competency_name:
            return False, "Competency Name field must be set!"
        elif display_order and not str(display_order).isdigit():
            return False, "Display Order field must be an integer!"
        elif expiry and not str(expiry).isdigit():
            return False, "Expiry field must be blank or an integer!"

        # If display order not set then set it to be after last row
        if not display_order:
            display_order = self.ad.md.get('Competency', 'Display Order', self.ad.md.len('Competency') - 1) + 1
        else:
            display_order = int(display_order)

        if expiry:
            expiry = int(expiry)

        try:
            self.ad.md.index('Competency', 'Competency Name', competency_name)
        except IndexError:
            self.ad.master_updated = True
            self.ad.md.add_row('Competency', {'Competency Name': competency_name,
                                              'Scope': scope,
                                              'Display Order': display_order,
                                              'Expiry': expiry,
                                              'Prerequisite': prerequisite,
                                              'Nightshift': nightshift,
                                              'Bank': bank})
            return True, f"Added {competency_name}"
        else:
            return False, f"Competency Name {competency_name} already defined!"
