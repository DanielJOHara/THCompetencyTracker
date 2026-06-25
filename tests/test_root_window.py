import pytest
from unittest.mock import patch, MagicMock
import os
import sys
from source.root_window import RootWindow


class RootWindowNoInit(RootWindow):
    def __init__(self, ad):
        self.ad = ad
        self.wnd_root = MagicMock()


@pytest.fixture
def mock_ad(ad_with_status):
    ad_with_status.args.readonly = False
    ad_with_status.args.theme = 'blue'
    ad_with_status.args.icon = 'icon.png'
    ad_with_status.args.master_excel_directory = 'C:\\data'
    ad_with_status.args.master_excel_file_name = 'master.xlsx'
    return ad_with_status


def test_root_window_set_button_states(mock_ad):
    app = RootWindowNoInit(mock_ad)
    app.btn_competency = MagicMock()
    app.btn_save = MagicMock()
    app.btn_data_input = MagicMock()
    
    app.set_button_states()
    
    app.btn_competency.configure.assert_called_with(state='normal')
    app.btn_save.configure.assert_called_with(state='normal')
    app.btn_data_input.configure.assert_called_with(state='normal')


@patch('source.root_window.ctk.CTk')
@patch('source.root_window.ctk.CTkFrame')
@patch('source.root_window.ctk.CTkButton')
@patch('source.root_window.ctk.CTkLabel')
@patch('source.root_window.resource')
@patch('source.root_window.os.path.isfile', return_value=True)
@patch('source.root_window.ImageTk.PhotoImage')
def test_root_window_init(mock_photo, mock_isfile, mock_resource, mock_label, mock_button, mock_frame, mock_ctk, mock_ad):
    # Mocking ctk.CTk instance to prevent real window creation
    root_instance = MagicMock()
    mock_ctk.return_value = root_instance
    
    app = RootWindow(mock_ad)
    
    assert app.wnd_root == root_instance
    assert mock_frame.called
    assert mock_button.call_count == 4
    assert mock_label.called
    root_instance.protocol.assert_called_with('WM_DELETE_WINDOW', app.on_closing)
    root_instance.after_idle.assert_called_with(app.on_startup)


@patch('source.root_window.os.access', return_value=True)
@patch('source.root_window.MasterData')
def test_root_window_on_startup_success(mock_md, mock_access, mock_ad):
    app = RootWindowNoInit(mock_ad)
    # Mock set_button_states to avoid errors if not all buttons are on 'app'
    app.set_button_states = MagicMock()
    
    app.on_startup()
    
    assert mock_ad.md is not None
    mock_md.return_value.load.assert_called_once()


@patch('source.root_window.os.access', return_value=True)
@patch('source.root_window.MasterData')
@patch('source.root_window.child_window')
def test_root_window_on_startup_readonly(mock_child, mock_md, mock_access, mock_ad):
    mock_ad.args.readonly = True
    app = RootWindowNoInit(mock_ad)
    app.set_button_states = MagicMock()
    
    app.on_startup()
    
    app.wnd_root.withdraw.assert_called_once()
    assert mock_child.called


@patch('source.root_window.os.access', return_value=True)
@patch('source.root_window.MasterData')
@patch('source.root_window.show_master_data_error')
def test_root_window_on_startup_master_data_error(mock_show_error, mock_md, mock_access, mock_ad):
    from source.master_data import MasterDataError
    mock_md.return_value.load.side_effect = MasterDataError("Test Error")
    app = RootWindowNoInit(mock_ad)
    
    app.on_startup()
    mock_show_error.assert_called_once()


@patch('source.root_window.os.access', return_value=True)
@patch('source.root_window.MasterData')
@patch('source.root_window.CTkMessagebox')
@patch('source.root_window.child_window')
def test_root_window_on_startup_io_error(mock_child, mock_msg, mock_md, mock_access, mock_ad):
    # First call to load raises IOError, second (after 'Read Only' choice) succeeds
    mock_md.return_value.load.side_effect = [IOError("Master Excel in use"), None]
    app = RootWindowNoInit(mock_ad)
    app.frm_button = MagicMock()
    mock_msg.return_value.get.return_value = 'Read Only'
    
    app.on_startup()
    assert mock_ad.args.readonly is True
    assert mock_child.called


@patch('source.root_window.os.access', return_value=False)
@patch('source.root_window.sys.exit')
@patch('source.root_window.CTkMessagebox')
def test_root_window_on_startup_no_access(mock_msg, mock_exit, mock_access, mock_ad):
    app = RootWindowNoInit(mock_ad)
    app.on_startup()
    mock_exit.assert_called_with(1)


def test_root_window_run(mock_ad):
    app = RootWindowNoInit(mock_ad)
    app.run()
    app.wnd_root.mainloop.assert_called_once()


def test_root_window_handle_save_click(mock_ad):
    app = RootWindowNoInit(mock_ad)
    mock_ad.md = MagicMock()
    mock_ad.master_updated = True
    
    with patch('source.root_window.CTkMessagebox'):
        app.handle_save_click()
    
    mock_ad.md.write.assert_called_once()
    assert mock_ad.master_updated is False


@patch('source.root_window.tk.filedialog.askopenfilename', return_value='C:\\new.xlsx')
def test_root_window_handle_reload_click(mock_file, mock_ad):
    app = RootWindowNoInit(mock_ad)
    mock_ad.md = MagicMock()
    app.set_button_states = MagicMock()
    
    app.handle_reload_click()
    mock_ad.md.load.assert_called_with('C:\\new.xlsx')


def test_root_window_on_closing_no_changes(mock_ad):
    app = RootWindowNoInit(mock_ad)
    mock_ad.master_updated = False
    app.on_closing()
    app.wnd_root.destroy.assert_called_once()


@patch('source.root_window.CTkMessagebox')
def test_root_window_on_closing_with_changes(mock_msg, mock_ad):
    app = RootWindowNoInit(mock_ad)
    mock_ad.master_updated = True
    mock_ad.md = MagicMock()
    
    # Case 1: Save Changes
    mock_msg.return_value.get.return_value = 'Save Changes'
    app.on_closing()
    mock_ad.md.write.assert_called_once()
    app.wnd_root.destroy.assert_called()
    
    # Case 2: Cancel
    app.wnd_root.destroy.reset_mock()
    mock_msg.return_value.get.return_value = 'Cancel'
    app.on_closing()
    app.wnd_root.destroy.assert_not_called()
