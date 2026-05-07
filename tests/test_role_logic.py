import pytest
import logging

from source.role_logic import RoleUpdateLogic

# Set up logging
logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


@pytest.fixture
def role_values(ad):
    role_values = []
    for db_r in range(ad.md.len('Role')):
        role_values.append({'Display Order': str(ad.md.get('Role', 'Display Order', db_r)),
                            'Role Code': ad.md.get('Role', 'Role Code', db_r),
                            'Role Name': ad.md.get('Role', 'Role Name', db_r),
                            'RN': ad.md.get('Role', 'RN', db_r)})
    yield role_values


def test_save_roles_no_changes(ad, role_values):
    """Test that save_roles returns 0 changes when no data is modified."""
    input_valid, changes, message = RoleUpdateLogic(ad).save_roles(role_values)

    assert input_valid
    assert changes == 0
    assert message == "0 Role changes saved"


def test_save_roles_invalid_display_order(ad, role_values):
    """Test that save_roles returns 0 changes when no data is modified."""
    role_values[0]['Display Order'] = 'X'
    input_valid, changes, message = RoleUpdateLogic(ad).save_roles(role_values)

    assert not input_valid
    assert changes == 0
    assert message == "Display Order field must be integer!"


def test_save_roles_with_changes(ad, role_values):
    """Test that save_roles correctly saves modified data."""
    role_values[0]['Role Name'] = "New Role Name"
    input_valid, changes, message = RoleUpdateLogic(ad).save_roles(role_values)

    assert changes == 1
    assert message == "1 Role changes saved"
    assert ad.md.get('Role', 'Role Name', 0) == "New Role Name"


def test_add_role_success(ad):
    """Test that a new role can be added successfully."""
    role_code = "NEW"
    role_name = "New Role"
    display_order = "100"
    rn = 1
    initial_len = ad.md.len('Role')
    success, message = RoleUpdateLogic(ad).add_role(role_code, role_name, display_order, rn)

    assert success is True
    assert message == f"Added {role_code} - {role_name}"
    assert ad.md.len('Role') == initial_len + 1


def test_add_role_duplicate(ad):
    """Test that adding a duplicate role fails."""
    role_code = "R1"  # Existing role code
    role_name = "Duplicate role"
    display_order = ""
    rn = 1

    success, message = RoleUpdateLogic(ad).add_role(role_code, role_name, display_order, rn)

    assert success is False
    assert message == f"Role Code {role_code} all ready defined!"


def test_delete_role_success(ad):
    """Test that a role can be deleted successfully."""
    # First add a role that has no dependencies
    ad.md.add_row('Role', {'Role Code': 'TEMP', 'Role Name': 'Temp Role', 'Display Order': 10, 'RN': 0})
    role_code_to_delete = "TEMP"
    success, warning, message = RoleUpdateLogic(ad).delete_role(role_code_to_delete)

    assert success is True
    assert warning is False
    assert message == f"{role_code_to_delete} deleted."
    assert ad.md.count('Role', 'Role Code', role_code_to_delete) == 0


def test_delete_role_with_dependents(ad):
    """Test that deleting a role with dependent records is handled correctly."""
    role_code_with_deps = "R2"  # This role has dependencies in the test data
    
    success, warning, message = RoleUpdateLogic(ad).delete_role(role_code_with_deps)
    assert success is False
    assert warning is True
    assert "is used" in message  # Check for the warning message

    # Now, test the actual deletion of dependents
    RoleUpdateLogic(ad).delete_role_with_dependents(role_code_with_deps)
    assert ad.md.count('Role', 'Role Code', role_code_with_deps) == 0
    assert ad.md.count('Staff Role', 'Role Code', role_code_with_deps) == 0
    assert ad.md.count('Role Competency', 'Role Code', role_code_with_deps) == 0
    assert ad.md.count('Role Service', 'Role Code', role_code_with_deps) == 0
