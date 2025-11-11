import pytest
import logging

from source.staff_logic import StaffLogic
from source.master_data import MasterData
from source.appdata import AppData
from source.window import date_to_string, parse_date

# Set up logging
logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


@pytest.fixture
def ad():
    ad = AppData()
    ad.md = MasterData('None', 30)
    ad.md.add_table('Staff',
                    ['Staff Name', 'Start Date', 'Practice Supervisor', 'Practice Assessor'],
                    [["Jane Smith", parse_date("2023-01-01"), 1, 0],
                     ["John Doe", parse_date("2023-02-01"), 0, 0],
                     ["Peter Jones", parse_date("2023-03-01"), 0, 1]])
    ad.md.add_table('Service',
                    ['Service Code', 'Service Name'],
                    [["IPS", "Inpatient Service"],
                     ["OPS", "Outpatient Service"]])
    ad.md.add_table('Role',
                    ['Role Code', 'Role Name'],
                    [["SN", "Staff Nurse"],
                     ["HCA", "Healthcare Assistant"]])
    ad.md.add_table('Staff Role',
                    ['Staff Name', 'Service Code', 'Role Code'],
                    [["Jane Smith", "OPS", "HCA"],
                     ["John Doe", "IPS", "SN"]])
    ad.md.add_table('Staff Competency',
                    ['Staff Name', 'Competency Name'],
                    [["John Doe", "VoED"]])
    yield ad


@pytest.fixture
def value_list(ad):
    value_list = []
    for db_s in range(ad.md.len('Staff')):
        value_list.append({'Staff Name': ad.md.get('Staff', 'Staff Name', db_s),
                           'Start Date': date_to_string(ad.md.get('Staff', 'Start Date', db_s)),
                           'Practice Supervisor': ad.md.get('Staff', 'Practice Supervisor', db_s),
                           'Practice Assessor': ad.md.get('Staff', 'Practice Assessor', db_s)})
    yield value_list


def test_add_staff_success(ad):
    """Test successfully adding a new staff member."""
    staff_len = ad.md.len('Staff')
    staff_name = "New Staff"
    start_date = "2023-01-01"
    practice_supervisor = 1
    practice_assessor = 0
    
    success, message = StaffLogic(ad).add_staff(staff_name, start_date, practice_supervisor, practice_assessor)
    
    assert success is True
    assert message == f"Added {staff_name}"
    assert ad.master_updated is True
    assert ad.md.len('Staff') == staff_len + 1


def test_add_staff_failure_exists(ad):
    """Test failing to add a staff member that already exists."""
    staff_len = ad.md.len('Staff')
    staff_name = ad.md.get('Staff', 'Staff Name', 0)
    start_date = "2023-01-01"
    practice_supervisor = 1
    practice_assessor = 0
    
    success, message = StaffLogic(ad).add_staff(staff_name, start_date, practice_supervisor, practice_assessor)
    
    assert success is False
    assert message == f"Staff Name {staff_name} is already defined!"
    assert ad.master_updated is False
    assert ad.md.len('Staff') == staff_len


def test_add_staff_failure_no_name(ad):
    """Test failing to add a staff member with no name."""
    staff_len = ad.md.len('Staff')
    staff_name = ""
    start_date = "2023-01-01"
    practice_supervisor = 1
    practice_assessor = 0

    success, message = StaffLogic(ad).add_staff(staff_name, start_date, practice_supervisor, practice_assessor)
    
    assert success is False
    assert message == "Staff Name field must be set!"
    assert ad.master_updated is False
    assert ad.md.len('Staff') == staff_len


def test_add_staff_failure_invalid_date(ad):
    """Test failing to add a staff member with an invalid date."""
    staff_len = ad.md.len('Staff')
    staff_name = "New Name"
    start_date = "2023-02-29"
    practice_supervisor = 1
    practice_assessor = 0
    success, message = StaffLogic(ad).add_staff(staff_name, start_date, practice_supervisor, practice_assessor)
    
    assert success is False
    assert message == f"Start Date {start_date} is not a valid date!"
    assert ad.master_updated is False
    assert ad.md.len('Staff') == staff_len


def test_delete_staff_success(ad):
    """Test successfully deleting a staff member."""
    staff_len = ad.md.len('Staff')
    staff_name = "Peter Jones"

    success, warning, message = StaffLogic(ad).delete_staff(staff_name)
    
    assert success is True
    assert warning is False
    assert message == f"{staff_name} deleted."
    assert ad.md.len('Staff') == staff_len - 1
    assert ad.md.count('Staff', 'Staff Name', staff_name) == 0


def test_delete_staff_failure_no_name(ad):
    """Test failing to delete a staff member with no name."""
    staff_len = ad.md.len('Staff')
    staff_name = ""

    success, warning, message = StaffLogic(ad).delete_staff(staff_name)
    
    assert success is False
    assert warning is False
    assert message == "No staff member selected."
    assert ad.md.len('Staff') == staff_len


def test_delete_staff_failure_with_dependents(ad):
    """Test failing to delete a staff member that has dependent records."""
    staff_len = ad.md.len('Staff')
    staff_name = "John Doe"
    sr_cnt = ad.md.count('Staff Role', 'Staff Name', staff_name)
    sc_cnt = ad.md.count('Staff Competency', 'Staff Name', staff_name)
    
    success, warning, message = StaffLogic(ad).delete_staff(staff_name)
    
    assert success is False
    assert warning is True
    assert f"{staff_name} is used {sr_cnt} times in Staff Role and {sc_cnt} times in Staff Competency" in message
    assert ad.md.len('Staff') == staff_len


def test_delete_staff_with_dependents(ad):
    """Test deleting a staff member and their dependent records."""
    staff_len = ad.md.len('Staff')
    staff_name = "John Doe"

    StaffLogic(ad).delete_staff_with_dependents(staff_name)

    assert ad.md.len('Staff') == staff_len - 1
    assert ad.md.count('Staff', 'Staff Name', staff_name) == 0


def test_save_staff_no_changes(ad, value_list):
    """Test saving staff when no changes have been made."""
    db_s_list = list(range(len(value_list)))
    number_changes, message = StaffLogic(ad).save_staff(value_list, db_s_list)

    assert number_changes == 0
    assert message == "0 changes saved"


def test_save_staff_no_changes_filtered_list(ad, value_list):
    """Test saving staff when no changes have been made when a row is filtered."""
    value_list.pop(1)
    db_s_list = list(range(len(value_list)))
    db_s_list.pop(1)
    number_changes, message = StaffLogic(ad).save_staff(value_list, db_s_list)

    assert number_changes == 0
    assert message == "0 changes saved"


def test_save_staff_with_name_change(ad, value_list):
    """Test saving staff when a name change has been made."""
    old_name = value_list[1]["Staff Name"]
    new_name = 'New Name'
    db_s_list = list(range(len(value_list)))
    value_list[1]["Staff Name"] = new_name

    number_changes, message = StaffLogic(ad).save_staff(value_list, db_s_list)
    
    assert number_changes == 1
    assert message == "1 changes saved"
    assert ad.master_updated is True
    assert ad.md.count('Staff', 'Staff Name', old_name) == 0
    assert ad.md.count('Staff', 'Staff Name', new_name) == 1
    assert ad.md.count('Staff Role', 'Staff Name', old_name) == 0
    assert ad.md.count('Staff Role', 'Staff Name', new_name) == 1
    assert ad.md.count('Staff Competency', 'Staff Name', old_name) == 0
    assert ad.md.count('Staff Competency', 'Staff Name', new_name) == 1


def test_apply_no_filters(ad):
    """Test applying no filters to the staff list."""
    name_filter = ""
    no_role_filter = 1
    service_filter = ad.md.get_list('Service', 'Service Code')
    role_filter = ad.md.get_list('Role', 'Role Code')

    db_s_list = StaffLogic(ad).apply_filters(name_filter, no_role_filter, service_filter, role_filter)

    assert db_s_list == list(range(ad.md.len("Staff")))


def test_apply_name_filters(ad):
    """Test applying name filter to the staff list."""
    name_filter = "jo"
    no_role_filter = 1
    service_filter = ad.md.get_list('Service', 'Service Code')
    role_filter = ad.md.get_list('Role', 'Role Code')

    db_s_list = StaffLogic(ad).apply_filters(name_filter, no_role_filter, service_filter, role_filter)

    assert db_s_list == [1, 2]


def test_apply_no_role_filters(ad):
    """Test applying no role filters to the staff list."""
    name_filter = ""
    no_role_filter = 0
    service_filter = ad.md.get_list('Service', 'Service Code')
    role_filter = ad.md.get_list('Role', 'Role Code')

    db_s_list = StaffLogic(ad).apply_filters(name_filter, no_role_filter, service_filter, role_filter)

    assert db_s_list == [0, 1]


def test_apply_role_filters(ad):
    """Test applying role filters to the staff list."""
    name_filter = ""
    no_role_filter = 0
    service_filter = ad.md.get_list('Service', 'Service Code')
    role_filter = ['HCA']

    db_s_list = StaffLogic(ad).apply_filters(name_filter, no_role_filter, service_filter, role_filter)

    assert db_s_list == [0]


def test_apply_service_filters(ad):
    """Test applying service filters to the staff list."""
    name_filter = ""
    no_role_filter = 0
    service_filter = ['IPS']
    role_filter = ad.md.get_list('Role', 'Role Code')

    db_s_list = StaffLogic(ad).apply_filters(name_filter, no_role_filter, service_filter, role_filter)

    assert db_s_list == [1]
