import pytest
import logging

from source.staff_role_logic import StaffRoleLogic
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
    ad.md.add_table('Staff',
                    ['Staff Name'],
                    [["Jane Smith"],
                     ["John Doe"],
                     ["Peter Jones"]])
    ad.md.add_table('Service',
                    ['Service Code', 'Service Name'],
                    [["IPS", "Inpatient Service"],
                     ["OPS", "Outpatient Service"],
                     ["MHS", "Mental Health Service"],
                     ["PCRT", "Primary Care Response Team"]])
    ad.md.add_table('Role',
                    ['Role Code', 'Role Name'],
                    [["SN", "Staff Nurse"],
                     ["HCA", "Healthcare Assistant"],
                     ["RN", "Registered Nurse"]])
    ad.md.add_table('Staff Role',
                    ['Staff Name', 'Service Code', 'Role Code', 'Bank', 'Nightshift'],
                    [["Jane Smith", "OPS", "HCA", 0, 0],
                     ["John Doe", "IPS", "SN", 1, 1]])
    yield ad


@pytest.fixture
def value_list(ad):
    """Fixture to create a list of staff role dictionaries for a staff member."""
    staff_name = "John Doe"
    value_list = []
    for db_sr in range(ad.md.len('Staff Role')):
        if ad.md.get('Staff Role', 'Staff Name', db_sr) == staff_name:
            value_list.append({
                'Service Code': ad.md.get('Staff Role', 'Service Code', db_sr),
                'Role Code': ad.md.get('Staff Role', 'Role Code', db_sr),
                'Bank': ad.md.get('Staff Role', 'Bank', db_sr),
                'Nightshift': ad.md.get('Staff Role', 'Nightshift', db_sr)
            })
    return staff_name, value_list


def create_role_lists_from_value_list(ad, value_list):
    """Helper function to create role lists from a value_list."""
    service_codes = ad.md.get_list('Service', 'Service Code')
    role_list = []
    bank_list = []
    nightshift_list = []
    for service_code in service_codes:
        role = next((d for d in value_list if d['Service Code'] == service_code), None)
        if role:
            role_list.append(role['Role Code'])
            bank_list.append(role['Bank'])
            nightshift_list.append(role['Nightshift'])
        else:
            role_list.append("")
            bank_list.append(0)
            nightshift_list.append(0)
    return role_list, bank_list, nightshift_list


def test_save_staff_roles(value_list, ad):
    """Test saving new, updated, and deleted staff roles."""
    staff_name, original_value_list = value_list

    # 1. No changes
    role_list, bank_list, nightshift_list = create_role_lists_from_value_list(ad, original_value_list)
    input_valid, num_changes, message = StaffRoleLogic(ad).save_staff_roles(staff_name, role_list,
                                                                            bank_list, nightshift_list)
    assert input_valid is True
    assert num_changes == 0
    assert message == "0 changes saved"

    # 2. Add a new role
    new_role = {'Service Code': 'MHS', 'Role Code': 'RN', 'Bank': 0, 'Nightshift': 1}
    updated_value_list = original_value_list + [new_role]
    role_list, bank_list, nightshift_list = create_role_lists_from_value_list(ad, updated_value_list)
    input_valid, num_changes, message = StaffRoleLogic(ad).save_staff_roles(staff_name, role_list,
                                                                            bank_list, nightshift_list)
    assert input_valid is True
    assert num_changes == 1
    assert message == "1 changes saved"
    db_sr = ad.md.find_two('Staff Role', 'MHS', 'Service Code', staff_name, 'Staff Name')
    assert db_sr > -1
    assert ad.md.get('Staff Role', 'Role Code', db_sr) == 'RN'

    # 3. Update an existing role
    updated_value_list[0]['Role Code'] = 'RN'
    role_list, bank_list, nightshift_list = create_role_lists_from_value_list(ad, updated_value_list)
    input_valid, num_changes, message = StaffRoleLogic(ad).save_staff_roles(staff_name, role_list,
                                                                            bank_list, nightshift_list)
    assert input_valid is True
    assert num_changes == 1
    assert message == "1 changes saved"
    db_sr = ad.md.find_two('Staff Role', 'IPS', 'Service Code', staff_name, 'Staff Name')
    assert ad.md.get('Staff Role', 'Role Code', db_sr) == 'RN'

    # 4. Delete a role
    deleted_value_list = [r for r in updated_value_list if r['Service Code'] != 'MHS']
    role_list, bank_list, nightshift_list = create_role_lists_from_value_list(ad, deleted_value_list)
    input_valid, num_changes, message = StaffRoleLogic(ad).save_staff_roles(staff_name, role_list,
                                                                            bank_list, nightshift_list)
    assert input_valid is True
    assert num_changes == 1
    assert message == "1 changes saved"
    db_sr = ad.md.find_two('Staff Role', 'MHS', 'Service Code', staff_name, 'Staff Name')
    assert db_sr == -1


def test_delete_staff_roles(ad):
    """Test deleting all roles for a staff member."""
    staff_name = "John Doe"
    staff_role_len = StaffRoleLogic(ad).ad.md.len('Staff Role')

    StaffRoleLogic(ad).delete_staff_roles(staff_name)

    assert StaffRoleLogic(ad).ad.md.len('Staff Role') == staff_role_len - 1
    db_sr = StaffRoleLogic(ad).ad.md.find_one('Staff Role', staff_name, 'Staff Name')
    assert db_sr == -1


def test_filter_staff_names(ad):
    """Test filtering staff names."""
    # Test with a filter that matches some names
    filtered_names = StaffRoleLogic(ad).filter_staff_names("Jo")
    assert "John Doe" in filtered_names
    assert "Peter Jones" in filtered_names

    # Test with a filter that matches no names
    filtered_names = StaffRoleLogic(ad).filter_staff_names("NonExistentName")
    assert len(filtered_names) == 0

    # Test with an empty filter
    all_names = StaffRoleLogic(ad).ad.md.get_list('Staff', 'Staff Name')
    filtered_names = StaffRoleLogic(ad).filter_staff_names("")
    assert len(filtered_names) == len(all_names)
