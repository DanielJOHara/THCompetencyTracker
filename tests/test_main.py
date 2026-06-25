import pytest
from unittest.mock import patch, MagicMock, ANY
from source.main import main


@patch('source.main.AppData')
@patch('source.main.command_line')
@patch('source.main.RootWindow')
@patch('source.main.write_json_configuration')
def test_main_readonly_false(mock_write_json, mock_root_window, mock_command_line, mock_app_data):
    # Setup mock ad object
    mock_ad = MagicMock()
    mock_ad.args.readonly = False
    mock_app_data.return_value = mock_ad
    
    # Execute main
    main()
    
    # Verify calls
    mock_app_data.assert_called_once()
    mock_command_line.assert_called_once_with(mock_ad, ANY)
    mock_root_window.assert_called_once_with(mock_ad)
    mock_write_json.assert_called_once_with(mock_ad)


@patch('source.main.AppData')
@patch('source.main.command_line')
@patch('source.main.RootWindow')
@patch('source.main.write_json_configuration')
def test_main_readonly_true(mock_write_json, mock_root_window, mock_command_line, mock_app_data):
    # Setup mock ad object
    mock_ad = MagicMock()
    mock_ad.args.readonly = True
    mock_app_data.return_value = mock_ad
    
    # Execute main
    main()
    
    # Verify calls
    mock_app_data.assert_called_once()
    mock_command_line.assert_called_once_with(mock_ad, ANY)
    mock_root_window.assert_called_once_with(mock_ad)
    # write_json_configuration should NOT be called if readonly is True
    mock_write_json.assert_not_called()
