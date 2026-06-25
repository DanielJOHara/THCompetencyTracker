import os
import sys
import json
import pytest
import logging
import configparser
from unittest.mock import patch, MagicMock, mock_open
from source.command_line import (command_line, get_version_number, resource,
                                 read_json_configuration, write_json_configuration)
from source.appdata import AppData


@pytest.fixture
def ad():
    return AppData()


@patch('source.command_line.os.getlogin')
@patch('source.command_line.os.getcwd')
@patch('source.command_line.argparse.ArgumentParser.parse_args')
@patch('source.command_line.setup_logger')
@patch('source.command_line.get_version_number', return_value='1.2.3')
@patch('source.command_line.read_json_configuration')
@patch('source.command_line.os.path.exists', return_value=False)
@patch('source.command_line.os.access', return_value=True)
def test_command_line_defaults(mock_access, mock_exists, mock_read_json, mock_get_ver,
                               mock_setup_log, mock_parse_args, mock_getcwd, mock_getlogin, ad):
    mock_getlogin.return_value = 'testuser'
    mock_getcwd.return_value = '/test/cwd'
    
    mock_args = MagicMock()
    for attr in ['master_excel_directory', 'master_excel_file_name', 'report_directory', 
                 'report_password', 'readonly', 'supervisor', 'logging_level', 
                 'logging_directory', 'logging_file_name', 'retention', 'theme', 'icon']:
        setattr(mock_args, attr, None)
    mock_parse_args.return_value = mock_args

    command_line(ad, "Test Description")

    assert ad.username == 'testuser'
    assert ad.app_version == '1.2.3'
    assert ad.args.master_excel_file_name == 'THCompetencyMaster.xlsx'
    assert ad.args.theme == 'green'


@patch('source.command_line.os.path.exists', return_value=True)
@patch('source.command_line.configparser.ConfigParser')
@patch('source.command_line.argparse.ArgumentParser.parse_args')
@patch('source.command_line.os.getlogin', return_value='user')
@patch('source.command_line.setup_logger')
def test_command_line_with_ini_full(mock_setup_log, mock_getlogin, mock_parse_args, mock_config_cls, mock_exists, ad):
    mock_args = MagicMock()
    for attr in ['master_excel_directory', 'master_excel_file_name', 'report_directory', 
                 'report_password', 'readonly', 'supervisor', 'logging_level', 
                 'logging_directory', 'logging_file_name', 'retention', 'theme', 'icon']:
        setattr(mock_args, attr, None)
    mock_parse_args.return_value = mock_args

    mock_config = {
        'args': {
            'theme': 'blue',
            'retention': '60',
            'readonly': 'True',
            'supervisor': '1',
            'logging_level': 'DEBUG',
            'master_excel_file_name': 'custom.xlsx'
        }
    }
    mock_config_obj = MagicMock()
    mock_config_obj.__contains__.side_effect = lambda k: k in mock_config
    mock_config_obj.__getitem__.side_effect = lambda k: mock_config[k]
    mock_config_cls.return_value = mock_config_obj

    with patch('source.command_line.get_version_number', return_value='1.0.0'):
        with patch('source.command_line.read_json_configuration'):
            with patch('source.command_line.os.access', return_value=True):
                command_line(ad, "Desc")

    assert ad.args.theme == 'blue'
    assert ad.args.retention == 60
    assert ad.args.readonly is True
    assert ad.args.supervisor is True
    assert ad.args.logging_level == 'DEBUG'
    assert ad.args.master_excel_file_name == 'custom.xlsx'


def test_read_json_configuration_errors(ad, caplog):
    caplog.set_level(logging.INFO)
    ad.status_dict = {i: {'colour': ''} for i in range(7)}
    ad.configuration_path = 'missing.json'
    
    # Case: File missing
    with patch('source.command_line.os.path.isfile', return_value=False):
        read_json_configuration(ad)
    assert "json configuration file does not exist" in caplog.text

    # Case: KeyError (missing status key)
    ad.configuration_path = 'invalid.json'
    invalid_data = {'out_of_date': '#111111'} # Missing other keys
    with patch('source.command_line.os.path.isfile', return_value=True):
        with patch('builtins.open', mock_open(read_data=json.dumps(invalid_data))):
            read_json_configuration(ad)
    assert "json configuration file key error" in caplog.text


@patch('source.command_line.sys')
def test_resource_mei(mock_sys):
    # Simulate MEI (frozen) environment
    mock_sys.executable = 'C:\\temp\\app.exe'
    with patch('source.command_line.__file__', '_MEI'):
        res = resource('sub\\file.txt')
        assert res == 'C:\\temp\\sub\\file.txt'


@patch('source.command_line.GetFileVersionInfo')
def test_get_version_number_success(mock_get_info):
    mock_get_info.return_value = {
        'FileVersionMS': 0x00010002, # 1.2
        'FileVersionLS': 0x00030004  # 3.4
    }
    # win32api logic: LOWORD(ms).HIWORD(ls).LOWORD(ls)
    # LOWORD(0x00010002) = 2
    # HIWORD(0x00030004) = 3
    # LOWORD(0x00030004) = 4
    # Expected: "2.3.4"
    assert get_version_number("dummy.exe") == "2.3.4"


@patch('source.command_line.GetFileVersionInfo')
def test_get_version_number_fail(mock_get_info):
    import pywintypes
    mock_get_info.side_effect = pywintypes.error(1, "func", "msg")
    assert get_version_number("dummy.exe") == "0.0.0"


def test_resource():
    res_path = resource("test.txt")
    assert "test.txt" in res_path
    assert os.path.isabs(res_path)


def test_read_json_configuration(ad):
    ad.status_dict = {i: {'colour': ''} for i in range(7)}
    ad.configuration_path = 'test.json'
    
    config_data = {
        'out_of_date': '#111111',
        'ft_needed': '#222222',
        'comp_needed': '#333333',
        'next_3_months': '#444444',
        'in_date': '#555555',
        'not_required': '#666666',
        'not_relevant': '#777777'
    }
    
    with patch('source.command_line.os.path.isfile', return_value=True):
        with patch('builtins.open', mock_open(read_data=json.dumps(config_data))):
            read_json_configuration(ad)
            
    assert ad.status_dict[0]['colour'] == '#111111'
    assert ad.status_dict[6]['colour'] == '#777777'


def test_write_json_configuration(ad, tmp_path):
    ad.status_dict = {
        0: {'colour': '#111111'},
        1: {'colour': '#222222'},
        2: {'colour': '#333333'},
        3: {'colour': '#444444'},
        4: {'colour': '#555555'},
        5: {'colour': '#666666'},
        6: {'colour': '#777777'}
    }
    ad.configuration_path = str(tmp_path / "config.json")
    
    write_json_configuration(ad)
    
    assert os.path.exists(ad.configuration_path)
    with open(ad.configuration_path) as f:
        data = json.load(f)
    assert data['out_of_date'] == '#111111'
