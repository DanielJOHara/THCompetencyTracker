import pytest
from unittest.mock import patch

import logging
import customtkinter as ctk
import _tkinter

from source.role_gui import RoleAdd, RoleDelete, RoleUpdate


def pump_events(wnd_root):
    while wnd_root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
        pass


# Set up logging
logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


@pytest.fixture
def mock_input_warning():
    with patch('source.role_gui.input_warning') as mock_warn:
        yield mock_warn


@pytest.fixture
def mock_ctk_messagebox():
    with patch('source.role_gui.CTkMessagebox') as mock_msgbox:
        mock_msgbox.return_value.get.return_value = 'OK'
        yield mock_msgbox

@pytest.fixture
def mock_child_window():
    with patch('source.role_gui.child_window') as mock_child:
        yield mock_child


def test_role_update(ctk_root, ad, mock_child_window):
    # Create role update window
    wnd_role_update = ctk.CTkToplevel(ctk_root)
    wnd_role_update.grab_set()

    # Populate role update window
    role_update = RoleUpdate(ad, wnd_role_update)
    pump_events(ctk_root)

    assert len(role_update.role_widgets) == ad.md.len('Role')


def test_role_add(ctk_root, mock_input_warning, mock_ctk_messagebox, ad, mock_child_window):
    # Create role add window
    wnd_role_add = ctk.CTkToplevel(ctk_root)
    wnd_role_add.grab_set()

    # Populate role add window
    role_add = RoleAdd(ad, wnd_role_add)
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
    db_r = ad.md.find_one('Role', 'NEW', 'Role Code')
    assert db_r > -1
    assert ad.md.get('Role', 'Role Name', db_r) == 'New Role'

    # Close role add window
    role_add.btn_exit.invoke()
    pump_events(ctk_root)


def test_role_delete(ctk_root, ad, mock_ctk_messagebox, mock_child_window):
    # Create role delete window
    wnd_role_delete = ctk.CTkToplevel(ctk_root)
    wnd_role_delete.grab_set()

    # Populate role delete window
    role_delete = RoleDelete(ad, wnd_role_delete)
    pump_events(ctk_root)

    # Select the role record and check the name updates correctly
    role_delete.cmb_role_code.set('R2')
    role_delete.refresh_role(None)
    pump_events(ctk_root)
    assert role_delete.ent_role_name.get() == 'Role Two'

    # Delete the record
    role_delete.btn_delete.invoke()
    pump_events(ctk_root)
    assert role_delete.cmb_role_code.get() == ''
    assert role_delete.ent_role_name.get() == ''
    # Initial was 2 (R1, R2), deleted R2 -> 1
    assert ad.md.len("Role") == 1
    db_r = ad.md.find_one('Role', 'R2', 'Role Code')
    assert db_r == -1

    role_delete.btn_exit.invoke()
    pump_events(ctk_root)
