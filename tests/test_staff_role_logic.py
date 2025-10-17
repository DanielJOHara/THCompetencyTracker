
import os
import pytest
from unittest.mock import MagicMock
from source.master_data import MasterData
from source.appdata import AppData
from source.staff_role_logic import StaffRoleLogic


@pytest.fixture
def app_data():
    """Fixture to create an AppData object with a MasterData instance."""
    test_data_path = os.path.join(os.path.dirname(__file__), 'TestMasterData.xlsx')
    md = MasterData(test_data_path, 30)
    try:
        md.load()
        ad = AppData()
        ad.md = md
        yield ad
    finally:
        md._unlock()


@pytest.fixture
def staff_role_logic(app_data):
    """Fixture to create a StaffRoleLogic instance."""
    return StaffRoleLogic(app_data)


def test_save_staff_roles_add_and_update(staff_role_logic):
    """Test saving new and updated staff roles."""
    staff_name = "John Smith"
    staff_role_logic.ad.md.add_row('Staff', {'Staff Name': staff_name, 'Service Code': 'IPS'})

    # Mock widgets
    role_widgets = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    bank_widgets = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    nightshift_widgets = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]

    # Service codes from test data
    service_codes = ['IPS', 'MHS', 'OPS', 'PCRT']

    # First, add a new role
    role_widgets[0].get.return_value = "SN"
    bank_widgets[0].get.return_value = 1
    nightshift_widgets[0].get.return_value = 0
    for i in range(1, 4):
        role_widgets[i].get.return_value = ""
        bank_widgets[i].get.return_value = 0
        nightshift_widgets[i].get.return_value = 0

    num_changes, message = staff_role_logic.save_staff_roles(staff_name, role_widgets, bank_widgets, nightshift_widgets)
    assert num_changes == 1
    assert message == "1 changes saved"
    db_sr = staff_role_logic.ad.md.find_two('Staff Role', service_codes[0], 'Service Code', staff_name, 'Staff Name')
    assert db_sr > -1
    assert staff_role_logic.ad.md.get('Staff Role', 'Role Code', db_sr) == "SN"

    # Then, update the same role
    role_widgets[0].get.return_value = "RN"
    num_changes, message = staff_role_logic.save_staff_roles(staff_name, role_widgets, bank_widgets, nightshift_widgets)
    assert num_changes == 1
    assert message == "1 changes saved"
    assert staff_role_logic.ad.md.get('Staff Role', 'Role Code', db_sr) == "RN"


def test_delete_staff_roles(staff_role_logic):
    """Test deleting all roles for a staff member."""
    staff_name = "John Smith"
    staff_role_logic.ad.md.add_row('Staff', {'Staff Name': staff_name, 'Service Code': 'IPS'})
    staff_role_logic.ad.md.add_row('Staff Role', {'Service Code': 'IPS', 'Staff Name': staff_name, 'Role Code': 'SN', 'Bank': 0, 'Nightshift': 0})

    staff_role_logic.delete_staff_roles(staff_name)

    db_sr = staff_role_logic.ad.md.find_two('Staff Role', 'IPS', 'Service Code', staff_name, 'Staff Name')
    assert db_sr == -1


def test_filter_staff_names(staff_role_logic):
    """Test filtering staff names."""
    # Test with a filter that matches some names
    filtered_names = staff_role_logic.filter_staff_names("Duck")
    assert "Huey Duck" in filtered_names
    assert "Dewey Duck" in filtered_names
    assert "Louie Duck" in filtered_names

    # Test with a filter that matches no names
    filtered_names = staff_role_logic.filter_staff_names("NonExistentName")
    assert len(filtered_names) == 0

    # Test with an empty filter
    all_names = staff_role_logic.ad.md.get_list('Staff', 'Staff Name')
    filtered_names = staff_role_logic.filter_staff_names("")
    assert len(filtered_names) == len(all_names)
