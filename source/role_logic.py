"""This module contains the business logic for managing roles."""
import logging
from source.appdata import AppData

logger = logging.getLogger(__name__)


class RoleUpdateLogic(object):
    """Business logic for managing roles."""
    def __init__(self, ad: AppData):
        """Initialise the RoleUpdateLogic class."""
        self.ad = ad

    def save_roles(self, role_widgets: list) -> tuple[int, str]:
        """Read all values in table and update the table object if any values have changed."""
        # Validate integer attribute
        for db_r in range(self.ad.md.len('Role')):
            if not role_widgets[db_r]['display_order'].get().isdigit():
                return 0, "Display Order field must be integer!"

        # Check every value to see if it has changed
        number_changes = 0
        for db_r in range(self.ad.md.len('Role')):
            # Propagate Role Code changes to foreign keys in Role Competency and Staff Role tables
            if self.ad.md.get('Role', 'Role Code', db_r) != role_widgets[db_r]['role_code'].get():
                self.ad.master_updated = True
                old = self.ad.md.get('Role', 'Role Code', db_r)
                new = role_widgets[db_r]['role_code'].get()
                self.ad.md.replace('Role Competency', 'Role Code', old, new)
                self.ad.md.replace('Staff Role', 'Role Code', old, new)

            # Update row if it has changed
            if (self.ad.md.get('Role', 'Display Order', db_r) != int(role_widgets[db_r]['display_order'].get())
                    or self.ad.md.get('Role', 'Role Code', db_r) != role_widgets[db_r]['role_code'].get()
                    or self.ad.md.get('Role', 'Role Name', db_r) != role_widgets[db_r]['role_name'].get()
                    or self.ad.md.get('Role', 'RN', db_r) != role_widgets[db_r]['rn'].get()):
                number_changes += 1
                self.ad.master_updated = True
                self.ad.md.update_row('Role', db_r, {'Display Order': int(role_widgets[db_r]['display_order'].get()),
                                                     'Role Code': role_widgets[db_r]['role_code'].get(),
                                                     'Role Name': role_widgets[db_r]['role_name'].get(),
                                                     'RN': role_widgets[db_r]['rn'].get()})

        if number_changes > 0:
            self.ad.md.sort_table('Role')

        return number_changes, f"{number_changes} changes saved"

    def delete_role(self, role_code: str) -> tuple[bool, str]:
        """Delete a role and its dependent records."""
        if not role_code:
            return False, "No role code selected."

        # Warn that dependent rows will be deleted
        rc_cnt = self.ad.md.count('Role Competency', 'Role Code', role_code)
        sr_cnt = self.ad.md.count('Staff Role', 'Role Code', role_code)
        if rc_cnt or sr_cnt:
            warn_text = f"{role_code} is used {rc_cnt} times in Role Competency and {sr_cnt} times in Staff Role"
            return False, warn_text

        self.delete_role_with_dependents(role_code)
        
        return True, f"{role_code} deleted."

    def delete_role_with_dependents(self, role_code: str):
        """Delete a role and its dependent records."""
        db_r = self.ad.md.index('Role', 'Role Code', role_code)

        # Delete row and dependent rows, note deletes not audited
        self.ad.master_updated = True
        self.ad.md.delete_row('Role', db_r)

        # Delete entries for Role Code in Role Competency table
        rc_cnt = self.ad.md.count('Role Competency', 'Role Code', role_code)
        if rc_cnt:
            self.ad.md.delete_value('Role Competency', 'Role Code', role_code)

        # Delete entries for Role Code in Staff Role dataframe
        sr_cnt = self.ad.md.count('Staff Role', 'Role Code', role_code)
        if sr_cnt:
            self.ad.md.delete_value('Staff Role', 'Role Code', role_code)

    def add_role(self, role_code: str, role_name: str, display_order: str, rn: int) -> tuple[bool, str]:
        """Add a new role."""
        if not role_code:
            return False, "Role Code field must be set!"
        elif display_order and not str(display_order).isdigit():
            return False, "Display Order field must be an integer!"

        # If display order not set then set it to be after last row
        if not display_order:
            display_order = self.ad.md.get('Role', 'Display Order', self.ad.md.len('Role') - 1) + 1
        else:
            display_order = int(display_order)

        # Find Role Code to update or add a new one
        try:
            self.ad.md.index('Role', 'Role Code', role_code)
        except IndexError:
            self.ad.master_updated = True
            self.ad.md.add_row('Role', {'Role Code': role_code,
                                        'Role Name': role_name,
                                        'Display Order': display_order,
                                        'RN': rn})
            return True, f"Added {role_code} - {role_name}"
        else:
            return False, f"Role Code {role_code} all ready defined!"
