import pytest

import logging

from source.service_logic import ServiceLogic
from source.master_data import MasterData
from source.appdata import AppData


# Set up logging
logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


@pytest.fixture
def ad():
    ad = AppData()
    ad.md = MasterData('None', 30)
    ad.md.add_table('Service',
                    ['Service Code', 'Service Name'],
                    [["SC1", "Service Code One"],
                     ["SC2", 'Service Code Two'],
                     ["SC3", "Service Code Three"]])
    ad.md.add_table('Staff Role',
                    ['Service Code'],
                    [["SC2"], ["SC3"]])
    ad.md.add_table('Role Competency',
                    ['Service Code'],
                    [["SC2"], ["SC3"]])
    yield ad


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
    service_code = ad.md.get('Service', 'Service Code', 1)
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
    service_code = "SC1"
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
    service_code = "SC2"
    success, warning, message = ServiceLogic(ad).delete_service(service_code)
    
    assert success is False
    assert warning is True
    assert message == f"{service_code} is used 1 times in Staff Role and 1 times in Role Competency"
    assert ad.md.len('Service') == service_len


def test_delete_service_with_dependents(ad):
    """Test deleting a service and its dependent records."""
    service_len = ad.md.len('Service')
    staff_role_len = ad.md.len('Staff Role')
    role_competency_len = ad.md.len('Role Competency')
    service_code = "SC2"
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
    value_list[0]['Service Code'] = 'SC1New'
    value_list[0]['Service Name'] = 'New Name'

    reported_changes = ServiceLogic(ad).save_services(value_list)

    # Table will be sorted on service code so changes must not change order for this test to work
    input_and_output_match = True
    for db_s in range(ad.md.len('Service')):
        if (value_list[db_s]['Service Code'] != ad.md.get('Service', 'Service Code', db_s)
           or value_list[db_s]['Service Name'] != ad.md.get('Service', 'Service Name', db_s)):
            input_and_output_match = False
            break

    assert reported_changes == 1
    assert input_and_output_match


def test_save_services_with_changes_and_dependencies(ad, value_list):
    """Test saving services with dependencies when changes have been made."""
    value_list[1]['Service Code'] = 'SC2New'
    value_list[1]['Service Name'] = 'New Name'

    reported_changes = ServiceLogic(ad).save_services(value_list)

    # Table will be sorted on service code so changes must not change order for this test to work
    input_and_output_match = True
    for db_s in range(ad.md.len('Service')):
        if (value_list[db_s]['Service Code'] != ad.md.get('Service', 'Service Code', db_s)
           or value_list[db_s]['Service Name'] != ad.md.get('Service', 'Service Name', db_s)):
            input_and_output_match = False
            break

    assert reported_changes == 1
    assert input_and_output_match is True
    assert ad.md.find_one('Staff Role', 'SC2New', 'Service Code') > -1
    assert ad.md.find_one('Role Competency', 'SC2New', 'Service Code') > -1
