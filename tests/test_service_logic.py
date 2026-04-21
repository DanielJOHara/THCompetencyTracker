import pytest
import logging
from source.service_logic import ServiceLogic

# Set up logging
logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


@pytest.fixture
def value_list(ad):
    value_list = []
    for db_s in range(ad.md.len('Service')):
        value_list.append({'Service Code': ad.md.get('Service', 'Service Code', db_s),
                           'Service Name': ad.md.get('Service', 'Service Name', db_s)})
    yield value_list


def test_add_service_success(ad):
    """Test successfully adding a new service."""
    service_len = ad.md.len('Service')
    service_code = "NEW"
    service_name = "New Service"
    success, message = ServiceLogic(ad).add_service(service_code, service_name)
    
    assert success is True
    assert message == f"Added {service_code} - {service_name}"
    assert ad.md.len('Service') == service_len + 1
    assert ad.master_updated is True


def test_add_service_failure_exists(ad):
    """Test failing to add a service that already exists."""
    service_len = ad.md.len('Service')
    service_code = ad.md.get('Service', 'Service Code', 1) # SC2
    success, message = ServiceLogic(ad).add_service(service_code, "Existing service code")
    
    assert success is False
    assert message == f"Service Code {service_code} all ready defined!"
    assert ad.md.len('Service') == service_len


def test_add_service_failure_no_code(ad):
    """Test failing to add a service with no service code."""
    service_len = ad.md.len('Service')
    success, message = ServiceLogic(ad).add_service("", "No Code Service")
    
    assert success is False
    assert message == "Service Code field must be set!"
    assert ad.md.len('Service') == service_len


def test_delete_service_success(ad):
    """Test successfully deleting a service."""
    service_len = ad.md.len('Service')
    # SC1 in conftest.py has 1 CompService, 1 RoleService, 1 StaffRole, 1 RoleComp
    # Wait, SC1 has:
    # Service: SC1
    # Role Service: R1-SC1
    # Competency Service: VoED-SC1, Cannulation-SC1
    # Staff Role: JohnDoe-R1-SC1
    # Role Competency: R1-VoED-SC1
    # So SC1 HAS dependents.
    # SC3 has NO dependents in conftest.py.
    service_code = "SC3"
    success, warning, message = ServiceLogic(ad).delete_service(service_code)
    
    assert success is True
    assert warning is False
    assert message == f"{service_code} deleted."
    assert ad.md.len('Service') == service_len - 1
    assert ad.master_updated is True


def test_delete_service_failure_no_code(ad):
    """Test failing to delete a service with no service code."""
    service_len = ad.md.len('Service')
    success, warning, message = ServiceLogic(ad).delete_service("")
    
    assert success is False
    assert warning is False
    assert message == "No service code selected."
    assert ad.md.len('Service') == service_len


def test_delete_service_failure_with_dependents(ad):
    """Test failing to delete a service that has dependent records."""
    service_len = ad.md.len('Service')
    service_code = "SC1" # Has dependents
    # SC1 has: 1 Role Service, 2 Competency Service, 1 Staff Role, 1 Role Competency
    success, warning, message = ServiceLogic(ad).delete_service(service_code)
    
    assert success is False
    assert warning is True
    # Message format: f"{service_code} is used {sr_cnt} times in Staff Role, {rc_cnt} times in Role Competency and {cs_cnt} times in Competency Service."
    expected_message = f"{service_code} is used 1 times in Staff Role, 1 times in Role Competency and 2 times in Competency Service."
    assert message == expected_message
    assert ad.md.len('Service') == service_len


def test_delete_service_with_dependents(ad):
    """Test deleting a service and its dependent records."""
    service_len = ad.md.len('Service')
    staff_role_len = ad.md.len('Staff Role')
    role_competency_len = ad.md.len('Role Competency')
    service_code = "SC1"
    ServiceLogic(ad).delete_service_with_dependents(service_code)
    
    assert ad.md.len('Service') == service_len - 1
    assert ad.md.len('Staff Role') == staff_role_len - 1
    assert ad.md.len('Role Competency') == role_competency_len - 1
    assert ad.master_updated is True


def test_save_services_no_changes(ad, value_list):
    reported_changes = ServiceLogic(ad).save_services(value_list)

    input_and_output_match = True
    for db_s in range(ad.md.len('Service')):
        if (value_list[db_s]['Service Code'] != ad.md.get('Service', 'Service Code', db_s)
           or value_list[db_s]['Service Name'] != ad.md.get('Service', 'Service Name', db_s)):
            input_and_output_match = False
            break

    assert reported_changes == 0
    assert input_and_output_match is True


def test_save_services_with_changes(ad, value_list):
    """Test saving services without dependencies when changes have been made."""
    # SC3 has no dependencies
    idx = ad.md.index('Service', 'Service Code', 'SC3')
    value_list[idx]['Service Code'] = 'SC3New'
    value_list[idx]['Service Name'] = 'New Name'

    reported_changes = ServiceLogic(ad).save_services(value_list)

    assert reported_changes == 1


def test_save_services_with_changes_and_dependencies(ad, value_list):
    """Test saving services with dependencies when changes have been made."""
    idx = ad.md.index('Service', 'Service Code', 'SC1')
    value_list[idx]['Service Code'] = 'SC1New'
    value_list[idx]['Service Name'] = 'New Name'

    reported_changes = ServiceLogic(ad).save_services(value_list)

    assert reported_changes == 1
    assert ad.md.find_one('Staff Role', 'SC1New', 'Service Code') > -1
    assert ad.md.find_one('Role Competency', 'SC1New', 'Service Code') > -1
    assert ad.md.find_one('Competency Service', 'SC1New', 'Service Code') > -1
