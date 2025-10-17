
import pytest
from unittest.mock import MagicMock, create_autospec
from source.service_logic import ServiceLogic
from source.appdata import AppData


@pytest.fixture
def mock_appdata():
    """Fixture to create a mocked AppData object."""
    app_data = create_autospec(AppData)
    app_data.md = MagicMock()
    return app_data


@pytest.fixture
def service_logic(mock_appdata):
    """Fixture to create a ServiceLogic instance with a mocked AppData object."""
    return ServiceLogic(mock_appdata)


def test_add_service_success(service_logic, mock_appdata):
    """Test successfully adding a new service."""
    mock_appdata.md.index.side_effect = IndexError
    service_code = "NEW"
    service_name = "New Service"
    
    success, message = service_logic.add_service(service_code, service_name)
    
    assert success is True
    assert message == f"Added {service_code} - {service_name}"
    mock_appdata.md.add_row.assert_called_once_with('Service', {'Service Code': service_code,
                                                                'Service Name': service_name})
    assert mock_appdata.master_updated is True


def test_add_service_failure_exists(service_logic, mock_appdata):
    """Test failing to add a service that already exists."""
    mock_appdata.md.index.return_value = 0
    service_code = "EXIST"
    service_name = "Existing Service"
    
    success, message = service_logic.add_service(service_code, service_name)
    
    assert success is False
    assert message == f"Service Code {service_code} all ready defined!"
    mock_appdata.md.add_row.assert_not_called()


def test_add_service_failure_no_code(service_logic):
    """Test failing to add a service with no service code."""
    success, message = service_logic.add_service("", "No Code Service")
    
    assert success is False
    assert message == "Service Code field must be set!"


def test_delete_service_success(service_logic, mock_appdata):
    """Test successfully deleting a service."""
    service_code = "DEL"
    mock_appdata.md.count.return_value = 0
    
    success, message = service_logic.delete_service(service_code)
    
    assert success is True
    assert message == f"{service_code} deleted."
    mock_appdata.md.index.assert_called_with('Service', 'Service Code', service_code)


def test_delete_service_failure_no_code(service_logic):
    """Test failing to delete a service with no service code."""
    success, message = service_logic.delete_service("")
    
    assert success is False
    assert message == "No service code selected."


def test_delete_service_failure_with_dependents(service_logic, mock_appdata):
    """Test failing to delete a service that has dependent records."""
    service_code = "DEP"
    mock_appdata.md.count.side_effect = [1, 2]  # 1 for Staff Role, 2 for Role Competency
    
    success, message = service_logic.delete_service(service_code)
    
    assert success is False
    assert f"{service_code} is used 1 times in Staff Role and 2 times in Role Competency" in message


def test_delete_service_with_dependents(service_logic, mock_appdata):
    """Test deleting a service and its dependent records."""
    service_code = "DEP"
    mock_appdata.md.index.return_value = 0
    mock_appdata.md.count.side_effect = [1, 1]  # Staff Role, Role Competency
    
    service_logic.delete_service_with_dependents(service_code)
    
    mock_appdata.md.delete_row.assert_called_once_with('Service', 0)
    mock_appdata.md.delete_value.assert_any_call('Staff Role', 'Service Code', service_code)
    mock_appdata.md.delete_value.assert_any_call('Role Competency', 'Service Code', service_code)
    assert mock_appdata.master_updated is True


def test_save_services_no_changes(service_logic, mock_appdata):
    mock_appdata.md.len.return_value = 1
    mock_appdata.md.get.side_effect = ["CODE1", "NAME1"]
    
    # Mocking the widget structure
    mock_widget = {'code': MagicMock(), 'name': MagicMock()}
    mock_widget['code'].get.return_value = "CODE1"
    mock_widget['name'].get.return_value = "NAME1"
    service_widgets = [mock_widget]
    
    number_changes = service_logic.save_services(service_widgets)
    
    assert number_changes == 0
    mock_appdata.md.sort_table.assert_not_called()


def test_save_services_with_changes(service_logic, mock_appdata):
    """Test saving services when changes have been made."""
    mock_appdata.md.len.return_value = 1
    mock_appdata.md.get.side_effect = ["CODE1", "NAME1"]
    
    # Mocking the widget structure
    mock_widget = {'code': MagicMock(), 'name': MagicMock()}
    mock_widget['code'].get.return_value = "CODE2"
    mock_widget['name'].get.return_value = "NAME2"
    service_widgets = [mock_widget]
    
    number_changes = service_logic.save_services(service_widgets)
    
    assert number_changes == 1
    mock_appdata.md.update_row.assert_called_once_with('Service', 0, {'Service Code': 'CODE2', 'Service Name': 'NAME2'})
    mock_appdata.md.replace.assert_any_call('Staff Role', 'Service Code', 'CODE1', 'CODE2')
    mock_appdata.md.replace.assert_any_call('Role Competency', 'Service Code', 'CODE1', 'CODE2')
    mock_appdata.md.sort_table.assert_called_once_with('Service')
    assert mock_appdata.master_updated is True
