
import os
import pytest
from source.master_data import MasterData
from source.role_logic import RoleUpdateLogic
from source.appdata import AppData


@pytest.fixture
def ad():
    """Fixture to create an AppData object with a MasterData instance."""
    test_data_path = os.path.join(os.path.dirname(__file__), 'TestMasterData.xlsx')
    app_data = AppData()
    app_data.md = MasterData(test_data_path, 30)
    try:
        app_data.md.load()
        yield app_data
    except OSError as e:
        pytest.skip(f"Skipping tests because of OSError: {e}")
    finally:
        app_data.md._unlock()


class MockWidget:
    """A mock widget class to simulate customtkinter widgets."""
    def __init__(self, value):
        self._value = value

    def get(self):
        return self._value


def test_save_roles_no_changes(ad):
    """Test that save_roles returns 0 changes when no data is modified."""
    rul = RoleUpdateLogic(ad)
    
    # Create mock widgets with original data
    role_widgets = []
    for i in range(ad.md.len('Role')):
        role_widgets.append({
            'display_order': MockWidget(str(ad.md.get('Role', 'Display Order', i))),
            'role_code': MockWidget(ad.md.get('Role', 'Role Code', i)),
            'role_name': MockWidget(ad.md.get('Role', 'Role Name', i)),
            'rn': MockWidget(ad.md.get('Role', 'RN', i))
        })

    changes, message = rul.save_roles(role_widgets)
    assert changes == 0
    assert message == "0 changes saved"


def test_save_roles_with_changes(ad):
    """Test that save_roles correctly saves modified data."""
    rul = RoleUpdateLogic(ad)
    
    # Create mock widgets with modified data
    role_widgets = []
    for i in range(ad.md.len('Role')):
        role_widgets.append({
            'display_order': MockWidget(str(ad.md.get('Role', 'Display Order', i))),
            'role_code': MockWidget(ad.md.get('Role', 'Role Code', i)),
            'role_name': MockWidget(ad.md.get('Role', 'Role Name', i)),
            'rn': MockWidget(ad.md.get('Role', 'RN', i))
        })
    
    # Modify one record
    role_widgets[0]['role_name']._value = "New Role Name"

    changes, message = rul.save_roles(role_widgets)
    assert changes == 1
    assert message == "1 changes saved"
    assert ad.md.get('Role', 'Role Name', 0) == "New Role Name"


def test_add_role_success(ad):
    """Test that a new role can be added successfully."""
    rul = RoleUpdateLogic(ad)
    
    role_code = "NEW"
    role_name = "New Role"
    display_order = "100"
    rn = 1
    
    initial_len = ad.md.len('Role')
    success, message = rul.add_role(role_code, role_name, display_order, rn)
    assert success is True
    assert message == f"Added {role_code} - {role_name}"
    assert ad.md.len('Role') == initial_len + 1


def test_add_role_duplicate(ad):
    """Test that adding a duplicate role fails."""
    rul = RoleUpdateLogic(ad)
    
    role_code = "SN"  # Existing role code
    role_name = "Senior Nurse"
    display_order = "10"
    rn = 1

    success, message = rul.add_role(role_code, role_name, display_order, rn)
    assert success is False
    assert message == f"Role Code {role_code} all ready defined!"


def test_delete_role_success(ad):
    """Test that a role can be deleted successfully."""
    rul = RoleUpdateLogic(ad)
    
    role_code_to_delete = "TEST"
    # Add a role to be deleted
    rul.add_role(role_code_to_delete, "Test Role", "100", 0)
    
    success, message = rul.delete_role(role_code_to_delete)
    assert success is True
    assert message == f"{role_code_to_delete} deleted."
    with pytest.raises(IndexError):
        ad.md.index('Role', 'Role Code', role_code_to_delete)


def test_delete_role_with_dependents(ad):
    """Test that deleting a role with dependent records is handled correctly."""
    rul = RoleUpdateLogic(ad)
    
    role_code_with_deps = "SN"  # This role has dependencies in the test data
    
    success, message = rul.delete_role(role_code_with_deps)
    assert success is False
    assert "is used" in message  # Check for the warning message

    # Now, test the actual deletion of dependents
    rul.delete_role_with_dependents(role_code_with_deps)
    with pytest.raises(IndexError):
        ad.md.index('Role', 'Role Code', role_code_with_deps)
    assert ad.md.count('Staff Role', 'Role Code', role_code_with_deps) == 0
    assert ad.md.count('Role Competency', 'Role Code', role_code_with_deps) == 0
