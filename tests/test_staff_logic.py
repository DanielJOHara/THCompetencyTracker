
import pytest
from unittest.mock import MagicMock, create_autospec
from source.staff_logic import StaffLogic
from source.window import parse_date
from source.appdata import AppData


@pytest.fixture
def mock_appdata():
    """Fixture to create a mocked AppData object."""
    app_data = create_autospec(AppData)
    app_data.md = MagicMock()
    return app_data


@pytest.fixture
def staff_logic(mock_appdata):
    """Fixture to create a StaffLogic instance with a mocked AppData object."""
    return StaffLogic(mock_appdata)


def test_add_staff_success(staff_logic, mock_appdata):
    """Test successfully adding a new staff member."""
    mock_appdata.md.index.side_effect = IndexError
    staff_name = "New Staff"
    start_date = "2023-01-01"
    practice_supervisor = 1
    practice_assessor = 0
    
    success, message = staff_logic.add_staff(staff_name, start_date, practice_supervisor, practice_assessor)
    
    assert success is True
    assert message == f"Added {staff_name}"
    mock_appdata.md.add_row.assert_called_once()
    assert mock_appdata.master_updated is True


def test_add_staff_failure_exists(staff_logic, mock_appdata):
    """Test failing to add a staff member that already exists."""
    mock_appdata.md.index.return_value = 0
    staff_name = "Existing Staff"
    start_date = "2023-01-01"
    practice_supervisor = 1
    practice_assessor = 0
    
    success, message = staff_logic.add_staff(staff_name, start_date, practice_supervisor, practice_assessor)
    
    assert success is False
    assert message == f"Staff Name {staff_name} is already defined!"
    mock_appdata.md.add_row.assert_not_called()


def test_add_staff_failure_no_name(staff_logic):
    """Test failing to add a staff member with no name."""
    success, message = staff_logic.add_staff("", "2023-01-01", 1, 0)
    
    assert success is False
    assert message == "Staff Name field must be set!"


def test_add_staff_failure_invalid_date(staff_logic):
    """Test failing to add a staff member with an invalid date."""
    success, message = staff_logic.add_staff("New Staff", "invalid date", 1, 0)
    
    assert success is False
    assert message == f"Start Date invalid date is not a valid date!"


def test_delete_staff_success(staff_logic, mock_appdata):
    """Test successfully deleting a staff member."""
    staff_name = "DEL"
    mock_appdata.md.count.return_value = 0
    
    success, message = staff_logic.delete_staff(staff_name)
    
    assert success is True
    assert message == f"{staff_name} deleted."
    mock_appdata.md.index.assert_called_with('Staff', 'Staff Name', staff_name)


def test_delete_staff_failure_no_name(staff_logic):
    """Test failing to delete a staff member with no name."""
    success, message = staff_logic.delete_staff("")
    
    assert success is False
    assert message == "No staff member selected."


def test_delete_staff_failure_with_dependents(staff_logic, mock_appdata):
    """Test failing to delete a staff member that has dependent records."""
    staff_name = "DEP"
    mock_appdata.md.count.side_effect = [1, 2]  # 1 for Staff Role, 2 for Staff Competency
    
    success, message = staff_logic.delete_staff(staff_name)
    
    assert success is False
    assert f"{staff_name} is used 1 times in Staff Role and 2 times in Staff Competency" in message


def test_delete_staff_with_dependents(staff_logic, mock_appdata):
    """Test deleting a staff member and their dependent records."""
    staff_name = "DEP"
    mock_appdata.md.index.return_value = 0
    
    staff_logic.delete_staff_with_dependents(staff_name)
    
    mock_appdata.md.delete_row.assert_called_once_with('Staff', 0)
    mock_appdata.md.delete_value.assert_any_call('Staff Role', 'Staff Name', staff_name)
    mock_appdata.md.delete_value.assert_any_call('Staff Competency', 'Staff Name', staff_name)
    assert mock_appdata.master_updated is True


def test_save_staff_no_changes(staff_logic, mock_appdata):
    """Test saving staff when no changes have been made."""
    mock_appdata.md.get.side_effect = ["Staff1", parse_date("2023-01-01"), 1, 0]
    
    mock_widget = {'name': MagicMock(), 'start_date': MagicMock(), 'supervisor': MagicMock(), 'assessor': MagicMock()}
    mock_widget['name'].get.return_value = "Staff1"
    mock_widget['start_date'].get.return_value = "2023-01-01"
    mock_widget['supervisor'].get.return_value = 1
    mock_widget['assessor'].get.return_value = 0
    staff_widgets = [mock_widget]
    db_s_list = [0]
    
    number_changes, message = staff_logic.save_staff(staff_widgets, db_s_list)
    
    assert number_changes == 0
    assert message == "0 changes saved"
    mock_appdata.md.update_row.assert_not_called()


def test_save_staff_with_changes(staff_logic, mock_appdata):
    """Test saving staff when changes have been made."""
    mock_appdata.md.get.side_effect = ["Staff1", "2023-01-01", 1, 0]
    mock_appdata.md.count.return_value = 0
    
    mock_widget = {'name': MagicMock(), 'start_date': MagicMock(), 'supervisor': MagicMock(), 'assessor': MagicMock()}
    mock_widget['name'].get.return_value = "Staff2"
    mock_widget['start_date'].get.return_value = "2023-01-02"
    mock_widget['supervisor'].get.return_value = 0
    mock_widget['assessor'].get.return_value = 1
    staff_widgets = [mock_widget]
    db_s_list = [0]
    
    number_changes, message = staff_logic.save_staff(staff_widgets, db_s_list)
    
    assert number_changes == 1
    assert message == "1 changes saved"
    mock_appdata.md.update_row.assert_called_once()
    mock_appdata.md.replace.assert_any_call('Staff Role', 'Staff Name', 'Staff1', 'Staff2')
    mock_appdata.md.replace.assert_any_call('Staff Competency', 'Staff Name', 'Staff1', 'Staff2')
    mock_appdata.md.sort_table.assert_called_once_with('Staff')
    assert mock_appdata.master_updated is True


def test_apply_filters(staff_logic, mock_appdata):
    """Test applying filters to the staff list."""
    mock_appdata.md.get_list.return_value = ["Staff1", "Staff2"]
    mock_appdata.md.count.return_value = 1
    mock_appdata.md.find_one.side_effect = [0, -1, 1, -1]
    mock_appdata.md.get.side_effect = ["ROLE1", "SERVICE1", "ROLE2", "SERVICE2"]
    
    db_s_list = staff_logic.apply_filters("Staff", 1, ["SERVICE1"], ["ROLE1"])
    
    assert db_s_list == [0]
