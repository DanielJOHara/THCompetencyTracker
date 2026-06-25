import os
import pandas as pd
import pytest
import customtkinter as ctk
import _tkinter
from source.window import parse_date
from unittest.mock import MagicMock, patch
from source.master_data import MasterData
from source.appdata import AppData


@pytest.fixture(autouse=True)
def mock_ctkmessagebox_global():
    """Globally mock CTkMessagebox to prevent UI popups during tests."""
    with patch('CTkMessagebox.CTkMessagebox') as mock:
        mock.return_value.get.return_value = 'OK'
        yield mock


@pytest.fixture(autouse=True)
def mock_os_startfile_global():
    """Globally mock os.startfile to prevent files from opening during tests."""
    with patch('os.startfile') as mock:
        yield mock


@pytest.fixture(scope="session")
def ctk_root():
    try:
        root = ctk.CTk()
        yield root
        root.destroy()
    except _tkinter.TclError:
        pytest.skip("Skipping GUI tests: No display available")


@pytest.fixture
def master_data_path(tmp_path):
    """Fixture to create a temporary Excel file with test data."""
    file_path = tmp_path / "TestMasterData.xlsx"
    
    # Define minimal data for tests
    data = {
        'Service': pd.DataFrame({
            'Display Order': [1, 2, 3, 4],
            'Service Name': ['In Patient Service', 'Staff Who Left', 'Out Patient Service', 'Hospice at Home'],
            'Service Code': ['IPS', 'LEFT', 'OPS', 'PCRT'],
            'Special': [0, 1, 0, 0],
            'User': ['Unknown']*4,
            'Change Date': ['Unknown']*4
        }),
        'Role': pd.DataFrame({
            'Role Name': ['Role One', 'Role Two'],
            'Role Code': ['R1', 'R2'],
            'Display Order': [1, 2],
            'RN': [1, 0],
            'User': ['Unknown']*2,
            'Change Date': ['Unknown']*2
        }),
        'Staff': pd.DataFrame({
            'Staff Name': ['A Staff', 'Captain Amelia', 'Z Staff', 'Huey Duck', 'Dewey Duck'],
            'Start Date': [parse_date("2023-01-01"), parse_date("2023-02-01"), parse_date("2023-03-01"),
                           parse_date("2023-04-01"), parse_date("2023-05-01")],
            'Practice Supervisor': [0, 1, 0, 0, 0],
            'Practice Assessor': [0, 1, 0, 0, 0],
            'User': ['Unknown']*5,
            'Change Date': ['Unknown']*5
        }),
        'Competency': pd.DataFrame({
            'Competency Name': ['VoED', 'Cannulation'],
            'Scope': ['BOTH', 'RN'],
            'Display Order': [1, 2],
            'Expiry': [2, 0],
            'Prerequisite': [0, 0],
            'Nightshift': [0, 0],
            'Bank': [0, 0],
            'User': ['Unknown']*2,
            'Change Date': ['Unknown']*2
        }),
        'Staff Role': pd.DataFrame({
            'Staff Name': ['A Staff', 'Captain Amelia'],
            'Role Code': ['R1', 'R2'],
            'Service Code': ['IPS', 'OPS'],
            'Bank': [0, 0],
            'Nightshift': [0, 0],
            'User': ['Unknown']*2,
            'Change Date': ['Unknown']*2
        }),
        'Role Competency': pd.DataFrame({
            'Role Code': ['R1', 'R2'],
            'Competency Name': ['VoED', 'Cannulation'],
            'Service Code': ['IPS', 'OPS'],
            'User': ['Unknown']*2,
            'Change Date': ['Unknown']*2
        }),
        'Staff Competency': pd.DataFrame({
            'Staff Name': ['Huey Duck', 'Dewey Duck'],
            'Competency Name': ['VoED', 'Cannulation'],
            'Prerequisite Date': [pd.NaT, pd.NaT],
            'Achieved': [1, 0],
            'Competency Date': [parse_date("2024-01-30"), pd.NaT],
            'Completed': [1, 0],
            'Notes': ['PD', ''],
            'Not Required': [0, 0],
            'Required': [0, 0],
            'User': ['dudlea', 'unknown'],
            'Change Date': [parse_date("2024-01-31"), pd.NaT]
        })
    }
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for sheet_name, df in data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
    return str(file_path)


@pytest.fixture
def md(master_data_path):
    """Fixture to provide a MasterData instance pointing to a temporary file."""
    md_instance = MasterData(master_data_path, 30)
    md_instance.load()
    yield md_instance
    md_instance._unlock()


@pytest.fixture
def ad():
    """Fixture to create an AppData object with a fully populated MasterData instance."""
    ad = AppData()
    ad.md = MasterData('None', 30)
    
    # Mock args
    ad.args = MagicMock()
    ad.args.readonly = False
    ad.args.supervisor = True
    
    # Service
    ad.md.add_table('Service',
                    ['Display Order', 'Service Name', 'Service Code', 'Special'],
                    [[1, "Service One", "SC1", 0],
                     [2, "Service Two", "SC2", 0],
                     [3, "Service Three", "SC3", 0]])
    
    # Role
    ad.md.add_table('Role',
                    ['Role Name', 'Role Code', 'RN', 'Display Order'],
                    [["Role One", "R1", 1, 1],
                     ["Role Two", "R2", 0, 2]])
    
    # Staff
    from source.window import parse_date
    ad.md.add_table('Staff',
                    ['Staff Name', 'Start Date', 'Practice Supervisor', 'Practice Assessor'],
                    [["John Doe", parse_date("2023-01-01"), 0, 0],
                     ["Jane Smith", parse_date("2023-02-01"), 1, 1]])
    
    # Competency
    ad.md.add_table('Competency',
                    ['Competency Name', 'Scope', 'Display Order', 'Expiry', 'Prerequisite', 'Nightshift', 'Bank'],
                    [["VoED", "BOTH", 1, 2, 0, 0, 0],
                     ["Cannulation", "RN", 2, 0, 0, 0, 0],
                     ["Phlebotomy", "HCA", 3, 2, 0, 0, 0]])
    
    # Role Service
    ad.md.add_table('Role Service',
                    ['Role Code', 'Service Code'],
                    [["R1", "SC1"], ["R2", "SC2"]])
    
    # Competency Service
    ad.md.add_table('Competency Service',
                    ['Competency Name', 'Service Code'],
                    [["VoED", "SC1"], ["VoED", "SC2"], ["Cannulation", "SC1"]])
    
    # Staff Role
    ad.md.add_table('Staff Role',
                    ['Staff Name', 'Role Code', 'Service Code', 'Bank', 'Nightshift'],
                    [["John Doe", "R1", "SC1", 0, 0],
                     ["Jane Smith", "R2", "SC2", 0, 0]])
    
    # Role Competency
    ad.md.add_table('Role Competency',
                    ['Role Code', 'Competency Name', 'Service Code'],
                    [["R1", "VoED", "SC1"]])
    
    # Staff Competency
    ad.md.add_table('Staff Competency',
                    ['Staff Name', 'Competency Name', 'Prerequisite Date', 'Achieved',
                     'Competency Date', 'Completed', 'Notes', 'Not Required', 'Required'],
                    [["John Doe", "VoED", "", 1, parse_date("2023-03-01"), 1, "", 0, 1]])
    
    return ad


@pytest.fixture
def ad_with_status(ad):
    """Fixture to add status_dict to the centralized ad fixture."""
    ad.status_dict = {
        0: {'title': "Out of Date", 'text': "Out of Date", 'colour': '#FF0000', 'default': '#FF0000'},
        1: {'title': "FT Needed", 'text': "Prerequisite Needed", 'colour': '#FFFF40', 'default': '#FFFF40'},
        2: {'title': "Competency Needed", 'text': "Competency Needed", 'colour': '#B7DEE8', 'default': '#B7DEE8'},
        3: {'title': "Next Three Months", 'text': "Within 3 Months", 'colour': '#FCD5B4', 'default': '#FCD5B4'},
        4: {'title': "In Date", 'text': "In Date", 'colour': '#D8E4BC', 'default': '#D8E4BC'},
        5: {'title': "Not Required", 'text': "Not Required For Role", 'colour': '#D9D9D9', 'default': '#D9D9D9'},
        6: {'title': "Not Relevant", 'text': "Not Relevant", 'colour': '#FFFFFF', 'default': '#FFFFFF'}}

    return ad
