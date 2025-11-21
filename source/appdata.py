"""This module defines the AppData (application data) class for the TH Competency Tracker
   tool that holds the master data and parameters for application."""
from argparse import Namespace

from customtkinter import CTk

from source.master_data import MasterData


class AppData:
    """Class to hold master data and parameters for application."""
    args: Namespace = None  # Namespace for argparse to populated with command line arguments
    app_name: str = ''  # Application name
    app_version = ''  # Application version
    status_dict: dict = None  # Dictionary to hold competency statuses and their attributes
    master_updated: bool = False  # Flag to be set when a change is made to the master data in the dataframe dictionary
    wnd_root: CTk = None  # Root window object used to pick up window icon
    configuration_path: str  # Path to json configuration file
    md: MasterData = None  # Master data object to hold staff competency data
