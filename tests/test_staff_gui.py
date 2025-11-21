import pytest
from unittest.mock import patch, MagicMock

import logging
import customtkinter as ctk
import _tkinter

from source.master_data import MasterData
from source.appdata import AppData
from source.staff_gui import StaffAdd, StaffDelete, StaffUpdate, StaffAssessorUpdate
from source.staff_logic import StaffLogic
from source.window import parse_date, date_to_string
from source.staff_role_gui import StaffRoleUpdate


def pump_events(wnd_root):
    while wnd_root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
        pass


# Set up logging
logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


@pytest.fixture(scope="module")
def ctk_root():
    try:
        root = ctk.CTk()
        yield root
        root.destroy()
    except _tkinter.TclError:
        pytest.skip("Skipping GUI tests: No display available")


@pytest.fixture
def ad(request):
    """Fixture to create an AppData object with a MasterData instance."""
    md = MasterData('None', 30)
    md.add_table('Staff',
                 ['Staff Name', 'Start Date', 'Practice Supervisor', 'Practice Assessor'],
                 [["Jane Smith", parse_date("2023-01-01"), 1, 0],
                  ["John Doe", parse_date("2023-02-01"), 0, 0],
                  ["Peter Jones", parse_date("2023-03-01"), 0, 1]])
    md.add_table('Service',
                 ['Service Code', 'Service Name'],
                 [["IPS", "Inpatient Service"],
                  ["OPS", "Outpatient Service"]])
    md.add_table('Role',
                 ['Role Code', 'Role Name', 'RN'],
                 [["SN", "Staff Nurse", 1],
                  ["HCA", "Healthcare Assistant", 0]])
    md.add_table('Staff Role',
                 ['Staff Name', 'Service Code', 'Role Code'],
                 [["Jane Smith", "OPS", "HCA"],
                  ["John Doe", "IPS", "SN"]])
    md.add_table('Staff Competency',
                 ['Staff Name', 'Competency Name'],
                 [["John Doe", "VoED"]])
    ad = AppData()
    ad.md = md
    ad.args = MagicMock()
    ad.args.readonly = False

    def finalizer():
        # No file to unlock as MasterData is mocked with 'None'
        pass

    request.addfinalizer(finalizer)
    return ad


@pytest.fixture
def mock_input_warning():
    with patch('source.staff_gui.input_warning') as mock_warn:
        yield mock_warn


@pytest.fixture
def mock_ctk_messagebox():
    with patch('source.staff_gui.CTkMessagebox') as mock_msgbox:
        yield mock_msgbox


@pytest.fixture
def mock_child_window():
    with patch('source.staff_gui.child_window') as mock_child:
        yield mock_child


def test_staff_update(ctk_root, ad):
    # Create staff update window
    wnd_staff_update = ctk.CTkToplevel(ctk_root)
    wnd_staff_update.grab_set()

    # Populate staff update window
    staff_update = StaffUpdate(ad, wnd_staff_update)
    staff_update.sl.ad.md = ad.md  # Pass the MasterData object directly
    pump_events(ctk_root)

    assert len(staff_update.ent_staff_name) == ad.md.len('Staff')

    # Test saving changes for the first staff member
    staff_update.ent_staff_name[1].delete(0, 9999)
    staff_update.ent_staff_name[1].insert(0, "Jonathan Doe")
    with patch('source.staff_gui.CTkMessagebox') as mock_msgbox:
        staff_update.handle_save_click()
        pump_events(ctk_root)
        mock_msgbox.assert_called_once_with(title="Information", message="1 changes saved", icon='info')
    assert ad.md.get('Staff', 'Staff Name', 1) == "Jonathan Doe"
    assert ad.md.count('Staff Role', 'Staff Name', "Jonathan Doe") == 1
    assert ad.md.count('Staff Competency', 'Staff Name', "Jonathan Doe") == 1


def test_staff_add(ctk_root, mock_input_warning, mock_ctk_messagebox, mock_child_window, ad):
    # Create staff add window
    wnd_staff_add = ctk.CTkToplevel(ctk_root)
    wnd_staff_add.grab_set()

    # Populate staff add window
    staff_add = StaffAdd(ad, wnd_staff_add)
    pump_events(ctk_root)

    # Blank input test
    staff_add.ent_staff_name.delete(0, 9999)
    staff_add.ent_start_date.delete(0, 9999)
    staff_add.handle_add_click()
    pump_events(ctk_root)
    mock_input_warning.assert_called_with(staff_add.wnd_staff_add, "Staff Name field must be set!")

    # Add new staff
    staff_add.ent_staff_name.delete(0, 9999)
    staff_add.ent_staff_name.insert(0, 'New Staff')
    staff_add.ent_start_date.delete(0, 9999)
    staff_add.ent_start_date.insert(0, '2024-01-01')
    staff_add.chc_practice_supervisor.select()
    staff_add.btn_add.invoke()
    pump_events(ctk_root)

    # Check staff role window call
    mock_child_window.assert_called_with(StaffRoleUpdate, ad, wnd_staff_add, "New Staff")

    # Check information message call
    mock_ctk_messagebox.assert_called_once_with(title='Information', message='Added New Staff', icon='info')

    # Find the new record
    db_s = ad.md.find_one('Staff', 'New Staff', 'Staff Name')
    assert db_s > -1
    assert ad.md.get('Staff', 'Start Date', db_s) == parse_date('2024-01-01')
    assert ad.md.get('Staff', 'Practice Supervisor', db_s) == 1

    # Close staff add window
    staff_add.btn_exit.invoke()
    pump_events(ctk_root)


def test_staff_delete(ctk_root, mock_ctk_messagebox, ad):
    # Create staff delete window
    wnd_staff_delete = ctk.CTkToplevel(ctk_root)
    wnd_staff_delete.grab_set()

    # Populate staff delete window
    staff_delete = StaffDelete(ad, wnd_staff_delete)
    staff_delete.sl = StaffLogic(ad)  # Ensure StaffLogic uses the same AppData object
    pump_events(ctk_root)

    # Select a staff record and check the start date, practice supervisor and practice assessor update correctly
    staff_len = ad.md.len("Staff")
    db_s = 1
    staff_name = ad.md.get('Staff', 'Staff Name', db_s)
    start_date = date_to_string(ad.md.get('Staff', 'Start Date', db_s))
    practice_supervisor = ad.md.get('Staff', 'Practice Supervisor', db_s)
    practice_assessor = ad.md.get('Staff', 'Practice Assessor', db_s)
    staff_delete.cmb_staff_name.set(staff_name)
    staff_delete.refresh_staff(None)
    pump_events(ctk_root)

    assert staff_delete.ent_start_date.get() == start_date
    assert staff_delete.chc_practice_supervisor.get() == practice_supervisor
    assert staff_delete.chc_practice_assessor.get() == practice_assessor

    # Delete the record
    staff_delete.sl.ad.md = ad.md  # Pass the MasterData object directly
    staff_delete.btn_delete.invoke()
    pump_events(ctk_root)
    sr_cnt = ad.md.count('Staff Role', 'Staff Name', staff_name)
    sc_cnt = ad.md.count('Staff Competency', 'Staff Name', staff_name)
    if sr_cnt or sc_cnt:
        message = f"{staff_name} is used {sr_cnt} times in Staff Role and {sc_cnt} times in Staff Competency"
        mock_ctk_messagebox.assert_called_once_with(
            title="Dependent Record Warning", message=message, icon='warning', option_1='Delete', option_2='Cancel')
    assert staff_delete.cmb_staff_name.get() == ''
    assert staff_name not in staff_delete.cmb_staff_name.cget("values")
    assert ad.md.find_one('Staff', staff_name, 'Staff Name') == -1
    assert ad.md.len("Staff") == staff_len - 1

    staff_delete.btn_exit.invoke()
    pump_events(ctk_root)


def test_staff_assessor_update(ctk_root, ad):
    # Create staff assessor update window
    wnd_staff_assessor = ctk.CTkToplevel(ctk_root)
    wnd_staff_assessor.grab_set()

    # Populate staff assessor update window
    db_s = 1
    staff_name = ad.md.get('Staff', 'Staff Name', db_s)
    practice_supervisor = ad.md.get('Staff', 'Practice Supervisor', db_s)
    practice_assessor = ad.md.get('Staff', 'Practice Assessor', db_s)
    staff_assessor_update = StaffAssessorUpdate(ad, wnd_staff_assessor, staff_name)
    pump_events(ctk_root)

    # Check initial state
    assert staff_assessor_update.ent_staff_name.get() == staff_name
    assert staff_assessor_update.chc_practice_supervisor.get() == practice_supervisor
    assert staff_assessor_update.chc_practice_assessor.get() == practice_assessor

    # Update assessor status
    staff_assessor_update.chc_practice_assessor.select()
    staff_assessor_update.handle_update_click()
    pump_events(ctk_root)
    assert ad.md.get('Staff', 'Practice Assessor', db_s) == 1

    # Close window
    staff_assessor_update.btn_exit.invoke()
    pump_events(ctk_root)
