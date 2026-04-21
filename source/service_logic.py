"""This module contains the business logic for managing services."""
import logging
from source.appdata import AppData
from source.master_data import MasterDataError
from source.window import show_master_data_error

logger = logging.getLogger(__name__)


class ServiceLogic(object):
    """Business logic for managing services."""
    def __init__(self, ad: AppData):
        """Initialise the ServiceLogic class."""
        self.ad = ad

    def save_services(self, service_values: list) -> int:
        """Read all values in table and update the table object if any values
           have changed."""
        number_changes = 0
        try:
            for db_s in range(self.ad.md.len('Service')):
                old_code = self.ad.md.get('Service', 'Service Code', db_s)
                new_code = service_values[db_s]['Service Code']

                # Propagate Service Code changes to foreign keys in Staff Role and Role Competency tables
                if old_code != new_code:
                    self.ad.master_updated = True
                    self.ad.md.replace('Staff Role', 'Service Code', old_code, new_code)
                    self.ad.md.replace('Role Competency', 'Service Code', old_code, new_code)
                    self.ad.md.replace('Competency Service', 'Service Code', old_code, new_code)

                if (old_code != new_code
                        or self.ad.md.get('Service', 'Service Name', db_s) != service_values[db_s]['Service Name']):
                    number_changes += 1
                    self.ad.master_updated = True
                    self.ad.md.update_row('Service', db_s, {'Service Code': service_values[db_s]['Service Code'],
                                                            'Service Name': service_values[db_s]['Service Name']})
            
            if number_changes > 0:
                self.ad.md.sort_table('Service')
        except MasterDataError as e:
            show_master_data_error(str(e), self.ad.wnd_root)

        return number_changes

    def delete_service(self, service_code: str) -> tuple[bool, bool, str]:
        """Delete a service and its dependent records."""
        if not service_code:
            return False, False, "No service code selected."

        # Warn that dependent rows will be deleted
        sr_cnt = self.ad.md.count('Staff Role', 'Service Code', service_code)
        rc_cnt = self.ad.md.count('Role Competency', 'Service Code', service_code)
        cs_cnt = self.ad.md.count('Competency Service', 'Service Code', service_code)
        if rc_cnt or sr_cnt:
            warn_text = (f"{service_code} is used {sr_cnt} times in Staff Role,"
                         f" {rc_cnt} times in Role Competency and {cs_cnt} times in Competency Service.")
            return False, True, warn_text

        self.delete_service_with_dependents(service_code)
        
        return True, False, f"{service_code} deleted."

    def delete_service_with_dependents(self, service_code: str):
        """Delete a service and its dependent records."""
        db_s = self.ad.md.index('Service', 'Service Code', service_code)

        # Delete row and dependent rows, note deletes not audited
        self.ad.master_updated = True
        self.ad.md.delete_row('Service', db_s)

        # Delete entries for Service Code in Staff Role dataframe
        self.ad.md.delete_value('Staff Role', 'Service Code', service_code)

        # Delete entries for Service Code in Role Competency table
        self.ad.md.delete_value('Role Competency', 'Service Code', service_code)

        # Delete entries for Service Code in Competency Service table
        self.ad.md.delete_value('Competency Service', 'Service Code', service_code)

    def add_service(self, service_code: str, service_name: str) -> tuple[bool, str]:
        """Add a new service."""
        if not service_code:
            return False, "Service Code field must be set!"

        # If name is blank default it to the code
        if not service_name:
            service_name = service_code

        # Check Service Code is not already defined
        try:
            self.ad.md.index('Service', 'Service Code', service_code)
        except IndexError:
            try:
                self.ad.master_updated = True
                self.ad.md.add_row('Service', {'Service Code': service_code, 'Service Name': service_name})
                return True, f"Added {service_code} - {service_name}"
            except MasterDataError as e:
                show_master_data_error(str(e), self.ad.wnd_root)
                return False, str(e)
        else:
            return False, f"Service Code {service_code} all ready defined!"
