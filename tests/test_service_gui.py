import pytest
from unittest.mock import patch

import logging
import customtkinter as ctk
import _tkinter

from source.appdata import AppData
from source.master_data import MasterData
from source.service_gui import ServiceAdd, ServiceDelete


def pump_events(wnd_root):
    while wnd_root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
        pass


# Set up logging
logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)

# Create root window
wnd_root = ctk.CTk()


@pytest.fixture
def ad():
    ad = AppData()
    ad.md = MasterData('TestMasterData.xlsx', 30)
    try:
        ad.md.load('TestMasterData.xlsx')
        yield ad
    except OSError as e:
        pytest.skip(f"Skipping tests because of OSError: {e}")
    finally:
        ad.md._unlock()


@pytest.fixture
def mock_input_warning():
    with patch('source.service_gui.input_warning') as mock_warn:
        yield mock_warn


@pytest.fixture
def mock_ctk_messagebox():
    with patch('source.service_gui.CTkMessagebox') as mock_msgbox:
        yield mock_msgbox


def test_service_add(mock_input_warning, mock_ctk_messagebox, ad):
    # Create service add window
    wnd_service_add = ctk.CTkToplevel()
    wnd_service_add.grab_set()

    # Populate service add window
    service_add = ServiceAdd(ad, wnd_service_add)
    pump_events(wnd_root)

    # Blank input test
    service_add.ent_service_code.delete(0, 9999)
    service_add.ent_service_name.delete(0, 9999)
    service_add.handle_add_click()
    pump_events(wnd_root)
    mock_input_warning.assert_called_with(service_add.wnd_service_add, "Service Code field must be set!")

    # Add new service
    service_add.ent_service_code.delete(0, 9999)
    service_add.ent_service_code.insert(0, 'NEW')
    service_add.ent_service_name.delete(0, 9999)
    service_add.ent_service_name.insert(0, 'New Service')
    service_add.btn_add.invoke()
    pump_events(wnd_root)

    # Check information message call
    mock_ctk_messagebox.assert_called_once_with(title='Information', message='Added NEW - New Service', icon='info')

    # Find the wew record
    db_s = ad.md.find_one('Service', 'NEW', 'Service Code')
    assert db_s > -1
    assert ad.md.get('Service', 'Service Name', db_s) == 'New Service'

    # Close service add window
    service_add.btn_exit.invoke()
    pump_events(wnd_root)


def test_service_delete(ad):
    # Create service delete window
    wnd_service_delete = ctk.CTkToplevel()
    wnd_service_delete.grab_set()

    # Populate service delete window
    service_delete = ServiceDelete(ad, wnd_service_delete)
    pump_events(wnd_root)

    # Select the out patient service record and check the name updates correctly
    service_delete.cmb_service_code.set('OPS')
    service_delete.refresh_service(None)
    pump_events(wnd_root)
    assert service_delete.ent_service_name.get() == 'Out Patient Service'

    # Delete the new record
    service_delete.btn_delete.invoke()
    pump_events(wnd_root)
    assert service_delete.cmb_service_code.get() == ''
    assert service_delete.ent_service_name.get() == ''
    db_s = ad.md.find_one('Service', 'OPS', 'Service Code')
    assert db_s == -1

    service_delete.btn_exit.invoke()
    pump_events(wnd_root)
