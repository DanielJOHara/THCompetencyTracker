"""This module contains the business logic for the competency management.

"""
import logging
from source.appdata import AppData

logger = logging.getLogger(__name__)

class CompetencyLogic:
    """Encapsulates the business logic for competency management."""

    def __init__(self, app_data: AppData):
        """Initializes the CompetencyLogic.

        Args:
            app_data: The application's data object.
        """
        self.ad = app_data

    def save_competencies(self, competency_widgets: list) -> tuple[int, str]:
        """Saves all changes made to the competencies.

        Args:
            competency_widgets: A list of widgets representing the competencies.

        Returns:
            A tuple containing the number of changes and a message.
        """
        # Validate integer attributes
        for db_c in range(self.ad.md.len('Competency')):
            if not competency_widgets[db_c]['display_order'].get().isdigit():
                return 0, "Display Order field must be integer!"
            if competency_widgets[db_c]['expiry'].get() and not competency_widgets[db_c]['expiry'].get().isdigit():
                return 0, "Expiry field must be integer or blank!"

        # Check every value to see if it has changed
        number_changes = 0
        for db_c in range(self.ad.md.len('Competency')):
            # Propagate Competency Name changes to foreign keys in other tables
            if self.ad.md.get('Competency', 'Competency Name', db_c) != competency_widgets[db_c]['competency_name'].get():
                self.ad.master_updated = True
                old = self.ad.md.get('Competency', 'Competency Name', db_c)
                new = competency_widgets[db_c]['competency_name'].get()
                self.ad.md.replace('Role Competency', 'Competency Name', old, new)
                self.ad.md.replace('Staff Competency', 'Competency Name', old, new)

            if competency_widgets[db_c]['expiry'].get():
                expiry = int(competency_widgets[db_c]['expiry'].get())
            else:
                expiry = ''
            if (self.ad.md.get('Competency', 'Competency Name', db_c) != competency_widgets[db_c]['competency_name'].get()
                    or self.ad.md.get('Competency', 'Display Order', db_c) != int(competency_widgets[db_c]['display_order'].get())
                    or self.ad.md.get('Competency', 'Scope', db_c) != competency_widgets[db_c]['scope'].get()
                    or self.ad.md.get('Competency', 'Prerequisite', db_c) != competency_widgets[db_c]['prerequisite'].get()
                    or self.ad.md.get('Competency', 'Nightshift', db_c) != competency_widgets[db_c]['nightshift'].get()
                    or self.ad.md.get('Competency', 'Bank', db_c) != competency_widgets[db_c]['bank'].get()):
                number_changes += 1
                self.ad.master_updated = True
                self.ad.md.update_row('Competency', db_c, {'Competency Name': competency_widgets[db_c]['competency_name'].get(),
                                                           'Display Order': int(competency_widgets[db_c]['display_order'].get()),
                                                           'Scope': competency_widgets[db_c]['scope'].get(),
                                                           'Expiry': expiry,
                                                           'Prerequisite': competency_widgets[db_c]['prerequisite'].get(),
                                                           'Nightshift': competency_widgets[db_c]['nightshift'].get(),
                                                           'Bank': competency_widgets[db_c]['bank'].get()})

        if number_changes > 0:
            self.ad.md.sort_table('Competency')

        return number_changes, f"{number_changes} changes saved"

    def delete_competency(self, competency_name: str) -> tuple[bool, str]:
        """Deletes a competency and its dependent records.

        Args:
            competency_name: The name of the competency to delete.

        Returns:
            A tuple containing a boolean indicating success and a message.
        """
        if not competency_name:
            return False, "No competency selected."

        # Warn that dependent rows will be deleted
        rc_cnt = self.ad.md.count('Role Competency', 'Competency Name', competency_name)
        sc_cnt = self.ad.md.count('Staff Competency', 'Competency Name', competency_name)
        if rc_cnt or sc_cnt:
            warn_text = (f"{competency_name} is used {rc_cnt} times in Role Competency"
                         f" and {sc_cnt} times in Staff Competency")
            return False, warn_text

        self.delete_competency_with_dependents(competency_name)
        return True, f"{competency_name} deleted."

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

    def add_competency(self, competency_name: str, scope: str, display_order: str, expiry: str, prerequisite: int,
                       nightshift: int, bank: int) -> tuple[bool, str]:
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
