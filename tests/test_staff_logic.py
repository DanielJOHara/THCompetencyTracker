import pytest
import logging
from source.staff_logic import StaffLogic
from source.window import date_to_string, parse_date

# Set up logging
logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


@pytest.fixture
def value_list(ad):
    value_list = []
    # ad.md is sorted by Staff Name
    # In conftest: John Doe (2023-01-01), Jane Smith (2023-02-01)
    # Sorted: Jane Smith follows John Doe? No, J, o, h, n vs J, a, n, e.
    # Jane Smith (J-a-n-e) comes BEFORE John Doe (J-o-h-n).
    # Wait, my previous thought was Jane Smith then John Doe.
    # Let's check: 'a' is before 'o'. So Jane Smith is index 0, John Doe is index 1.
    # If [1] == [0] failed in test_apply_name_filters "smith", it means "smith" was at index 1?
    # No, if [1] == [0] failed, it means db_s_list was [1] and expected was [0].
    # So "smith" (Jane Smith) is at index 1?
    # "Jane Smith" vs "John Doe": J-a vs J-o. 'a' < 'o'. Jane Smith should be 0.
    # UNLESS case sensitivity? MasterData uses default pandas sorting.
    # Let me re-verify: Jane Smith vs John Doe. Jane is indeed before John.
    # Why did test_apply_name_filters "smith" return [1]?
    # Maybe because John Doe was updated to Jonathan Doe? No, they are fresh fixtures.
    # Let me check conftest.py again.
    # "John Doe", "Jane Smith".
    # Wait! If I add them in that order, and it sorts...
    # Let's just use find_one to be sure in the tests where possible, or fix the expectation.
    for db_s in range(ad.md.len('Staff')):
        value_list.append({'Staff Name': ad.md.get('Staff', 'Staff Name', db_s),
                           'Start Date': date_to_string(ad.md.get('Staff', 'Start Date', db_s)),
                           'Practice Supervisor': ad.md.get('Staff', 'Practice Supervisor', db_s),
                           'Practice Assessor': ad.md.get('Staff', 'Practice Assessor', db_s)})
    yield value_list


def test_add_staff_success(ad):
    """Test successfully adding a new staff member."""
    staff_len = ad.md.len('Staff')
    staff_name = " new  staff "
    start_date = "2023-01-01"
    practice_supervisor = 1
    practice_assessor = 0
    
    success, staff_name, message = StaffLogic(ad).add_staff(staff_name, start_date,
                                                            practice_supervisor, practice_assessor)
    assert staff_name == "New Staff"
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
    
    success, staff_name, message = StaffLogic(ad).add_staff(staff_name, start_date,
                                                            practice_supervisor, practice_assessor)
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

    success, staff_name, message = StaffLogic(ad).add_staff(staff_name, start_date,
                                                            practice_supervisor, practice_assessor)
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
    success, staff_name, message = StaffLogic(ad).add_staff(staff_name, start_date,
                                                            practice_supervisor, practice_assessor)
    assert success is False
    assert message == f"Start Date {start_date} is not a valid date!"
    assert ad.master_updated is False
    assert ad.md.len('Staff') == staff_len


def test_delete_staff_success(ad):
    """Test successfully deleting a staff member."""
    # Add a fresh staff with no dependencies
    ad.md.add_row('Staff', {'Staff Name': 'No Dep Staff', 'Start Date': parse_date('2023-01-01'), 
                           'Practice Supervisor': 0, 'Practice Assessor': 0})
    staff_len = ad.md.len('Staff')
    staff_name = "No Dep Staff"

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
    # John Doe has dependents (R1-SC1)
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
    db_s_list = list(range(len(value_list) + 1))
    db_s_list.pop(1)
    number_changes, message = StaffLogic(ad).save_staff(value_list, db_s_list)

    assert number_changes == 0
    assert message == "0 changes saved"


def test_save_staff_with_name_change(ad, value_list):
    """Test saving staff when a name change has been made."""
    idx = 0
    old_name = value_list[idx]["Staff Name"]
    new_name = 'New Name'
    db_s_list = list(range(len(value_list)))
    value_list[idx]["Staff Name"] = new_name

    number_changes, message = StaffLogic(ad).save_staff(value_list, db_s_list)
    
    assert number_changes == 1
    assert message == "1 changes saved"
    assert ad.master_updated is True
    assert ad.md.count('Staff', 'Staff Name', old_name) == 0
    assert ad.md.count('Staff', 'Staff Name', new_name) == 1
    # Check that Staff Role and Staff Competency were updated
    assert ad.md.count('Staff Role', 'Staff Name', new_name) > 0 or ad.md.count('Staff Competency', 'Staff Name', new_name) > 0


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
    name_filter = "smith"
    no_role_filter = 1
    service_filter = ad.md.get_list('Service', 'Service Code')
    role_filter = ad.md.get_list('Role', 'Role Code')

    db_s_list = StaffLogic(ad).apply_filters(name_filter, no_role_filter, service_filter, role_filter)

    expected_idx = ad.md.find_one('Staff', 'Jane Smith', 'Staff Name')
    assert db_s_list == [expected_idx]


def test_apply_no_role_filters(ad):
    """Test applying no role filters to the staff list."""
    # Add a staff member with no role
    ad.md.add_row('Staff', {'Staff Name': 'No Role Staff', 'Start Date': parse_date('2023-01-01'), 
                           'Practice Supervisor': 0, 'Practice Assessor': 0})
    
    name_filter = ""
    no_role_filter = 1
    service_filter = ad.md.get_list('Service', 'Service Code')
    role_filter = []

    db_s_list = StaffLogic(ad).apply_filters(name_filter, no_role_filter, service_filter, role_filter)

    idx = ad.md.find_one('Staff', 'No Role Staff', 'Staff Name')
    assert idx in db_s_list


def test_apply_role_filters(ad):
    """Test applying role filters to the staff list."""
    name_filter = ""
    no_role_filter = 0
    service_filter = ad.md.get_list('Service', 'Service Code')
    role_filter = ['R1']

    db_s_list = StaffLogic(ad).apply_filters(name_filter, no_role_filter, service_filter, role_filter)

    expected_idx = ad.md.find_one('Staff', 'John Doe', 'Staff Name')
    assert db_s_list == [expected_idx]


def test_apply_service_filters(ad):
    """Test applying service filters to the staff list."""
    name_filter = ""
    no_role_filter = 0
    service_filter = ['SC2']
    role_filter = ad.md.get_list('Role', 'Role Code')

    db_s_list = StaffLogic(ad).apply_filters(name_filter, no_role_filter, service_filter, role_filter)

    expected_idx = ad.md.find_one('Staff', 'Jane Smith', 'Staff Name')
    assert db_s_list == [expected_idx]
