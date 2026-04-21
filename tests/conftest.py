import pytest
import customtkinter as ctk
import _tkinter
from unittest.mock import MagicMock
from source.master_data import MasterData
from source.appdata import AppData


@pytest.fixture(scope="session")
def ctk_root():
    try:
        root = ctk.CTk()
        yield root
        root.destroy()
    except _tkinter.TclError:
        pytest.skip("Skipping GUI tests: No display available")


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
                    ['Service Name', 'Service Code'],
                    [["Service One", "SC1"],
                     ["Service Two", "SC2"],
                     ["Service Three", "SC3"]])
    
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
