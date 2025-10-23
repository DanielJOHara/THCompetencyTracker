import pytest
from unittest.mock import patch
import pandas as pd

import logging
import customtkinter as ctk
import _tkinter

from source.master_data import MasterData
from source.appdata import AppData
from source.role_gui import RoleAdd, RoleDelete, RoleUpdate


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
def app_data(request):
    """Fixture to create an AppData object with a MasterData instance."""
    ad = AppData()
    ad.md = MasterData('None', 30)
    ad.md.add_table('Role',
                    ['Role Code', 'Role Name', 'RN', 'Display Order'],
                    [["RC1", "Role Code One", 0, 1],
                     ["RC2", 'Role Code Two', 1, 2],
                     ["RC3", "Role Code Three", 0, 3]])

    def finalizer():
        # No file to unlock as MasterData is mocked with 'None'
        pass

    request.addfinalizer(finalizer)
    return ad


@pytest.fixture
def mock_input_warning():
    with patch('source.role_gui.input_warning') as mock_warn:
        yield mock_warn


@pytest.fixture
def mock_ctk_messagebox():
    with patch('source.role_gui.CTkMessagebox') as mock_msgbox:
        yield mock_msgbox


def test_role_update(ctk_root, app_data):
    # Create role update window
    wnd_role_update = ctk.CTkToplevel(ctk_root)
    wnd_role_update.grab_set()

    # Populate role update window
    role_update = RoleUpdate(app_data, wnd_role_update)
    pump_events(ctk_root)

    assert len(role_update.role_widgets) == app_data.md.len('Role')


def test_role_add(ctk_root, mock_input_warning, mock_ctk_messagebox, app_data):
    # Create role add window
    wnd_role_add = ctk.CTkToplevel(ctk_root)
    wnd_role_add.grab_set()

    # Populate role add window
    role_add = RoleAdd(app_data, wnd_role_add)
    pump_events(ctk_root)

    # Blank input test
    role_add.ent_role_code.delete(0, 9999)
    role_add.ent_role_name.delete(0, 9999)
    role_add.handle_add_click()
    pump_events(ctk_root)
    mock_input_warning.assert_called_with(role_add.wnd_role_add, "Role Code field must be set!")

    # Add new role
    role_add.ent_role_code.delete(0, 9999)
    role_add.ent_role_code.insert(0, 'NEW')
    role_add.ent_role_name.delete(0, 9999)
    role_add.ent_role_name.insert(0, 'New Role')
    role_add.btn_add.invoke()
    pump_events(ctk_root)

    # Check information message call
    mock_ctk_messagebox.assert_called_once_with(title='Information', message='Added NEW - New Role', icon='info')

    # Find the new record
    db_r = app_data.md.find_one('Role', 'NEW', 'Role Code')
    assert db_r > -1
    assert app_data.md.get('Role', 'Role Name', db_r) == 'New Role'

    # Close role add window
    role_add.btn_exit.invoke()
    pump_events(ctk_root)


def test_role_delete(ctk_root, app_data):
    # Create role delete window
    wnd_role_delete = ctk.CTkToplevel(ctk_root)
    wnd_role_delete.grab_set()

    # Populate role delete window
    role_delete = RoleDelete(app_data, wnd_role_delete)
    pump_events(ctk_root)

    # Select the role record and check the name updates correctly
    role_delete.cmb_role_code.set('RC2')
    role_delete.refresh_role(None)
    pump_events(ctk_root)
    assert role_delete.ent_role_name.get() == 'Role Code Two'

    # Delete the record
    role_delete.btn_delete.invoke()
    pump_events(ctk_root)
    assert role_delete.cmb_role_code.get() == ''
    assert role_delete.ent_role_name.get() == ''
    assert app_data.md.len("Role") == 2
    db_r = app_data.md.find_one('Role', 'RC2', 'Role Code')
    assert db_r == -1

    role_delete.btn_exit.invoke()
    pump_events(ctk_root)
