""" Module processes command line options for TH Competency Tracker and set up logging. This
    module also provides routines to write and read a json configuration file and a routine to
    add path to executable/script directory."""
import argparse
import configparser
import json
import logging
import os
import sys

import pywintypes
from win32api import GetFileVersionInfo, LOWORD, HIWORD

from source.appdata import AppData
from source.setup_logger import setup_logger

logger = logging.getLogger(__name__)


def command_line(ad: AppData, description: str) -> None:
    """Function to process command line parameters and set up the logger.
       It parses the command line using argparse and adds args, an argument
       object to the AppData object supplied."""

    if '_MEI' in __file__ or '_internal' in __file__:
        app_path = os.path.abspath(sys.executable)
        ad.app_name = os.path.basename(sys.executable).rsplit('.', 1)[0]
    else:
        app_path = os.path.abspath(__file__)
        ad.app_name = 'CompetencyTracker'

    app_directory = os.path.dirname(app_path)
    ad.username = os.getlogin().lower()
    current_directory = os.getcwd()

    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    themes = ['green', 'blue', 'dark-blue']

    # Put doc string in help
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        '-md',
        '--master_excel_directory',
        help="Master Excel directory, default application location")

    parser.add_argument(
        '-mf',
        '--master_excel_file_name',
        help="Master Excel file name, default THCompetencyMaster.xlsx")

    parser.add_argument(
        '-r',
        '--report_directory',
        help="Directory to output reports, default current directory")

    parser.add_argument(
        '-rp',
        '--report_password',
        help="Report password to remove sheet protection, default E***********1")

    parser.add_argument(
        '-ro',
        '--readonly',
        action="store_true",
        help="Run application in read only mode")

    parser.add_argument(
        '-s',
        '--supervisor',
        action="store_true",
        help="Display Practice Supervisor field")

    parser.add_argument(
        '-l',
        '--logging_level',
        type=str.upper,
        choices=log_levels,
        help="Logging level")

    parser.add_argument(
        '-ld',
        '--logging_directory',
        help="Logging file directory, default Master Excel Directory")

    parser.add_argument(
        '-lf',
        '--logging_file_name',
        help=f"Logging file name, default {ad.app_name}.log")

    parser.add_argument(
        '-re',
        '--retention',
        type=int,
        help=f"Retention period for archive Master Excel files, default 30 days")

    parser.add_argument(
        '-t',
        '--theme',
        type=str.lower,
        choices=themes,
        help="GUI theme colour")

    parser.add_argument(
        '-i',
        '--icon',
        help=f"Icon file for top left hand of windows, default Th.png")

    ad.args = parser.parse_args()

    ad.ini_path = str(os.path.join(app_directory, f'{ad.app_name}.ini'))

    # Load the ini file if it exists
    config = configparser.ConfigParser()
    if os.path.exists(ad.ini_path):
        config.read(ad.ini_path)

    def str_arg(arg: str, arg_name: str, config: configparser.ConfigParser, default: str | None,
                lower: bool = False, upper: bool = False) -> str:
        """Process a string argument."""
        if arg:
            return arg
        if ('args' in config
                and arg_name in config['args']
                and config['args'][arg_name]):
            if lower:
                return config['args'][arg_name].lower()
            if upper:
                return config['args'][arg_name].upper()
            return config['args'][arg_name]
        return default

    def int_arg(arg: int, arg_name: str, config: configparser.ConfigParser, default: int) -> int:
        """Process an integer argument."""
        if arg:
            return arg
        if ('args' in config
                and arg_name in config['args']
                and config['args'][arg_name]
                and config['args'][arg_name].isdigit()):
            return int(config['args'][arg_name])
        return default

    def list_arg(arg: str, arg_name: str, config: configparser.ConfigParser, choices: list, default: str,
                 lower: bool = False, upper: bool = False) -> str:
        """Process an argument with a list of choices."""
        if arg:
            return arg
        if ('args' in config
                and arg_name in config['args']
                and config['args'][arg_name]
                and config['args'][arg_name] in choices):
            if lower:
                return config['args'][arg_name].lower()
            if upper:
                return config['args'][arg_name].upper()
            return config['args'][arg_name]
        return default

    def bool_arg(arg: bool, arg_name: str, config: configparser.ConfigParser) -> bool:
        """Process a boolean argument."""
        if arg:
            return arg
        if ('args' in config
                and arg_name in config['args']
                and config['args'][arg_name]
                and config['args'][arg_name].upper() in ['Y', 'YES', 'TRUE', 'T', '1']):
            return True
        return False

    # For each command line argument if it is not set use the value
    # from ini file if that is also not set use the default value
    ad.args.master_excel_directory = str_arg(
        ad.args.master_excel_directory, 'master_excel_directory', config, app_directory)
    ad.args.master_excel_file_name = str_arg(
        ad.args.master_excel_file_name, 'master_excel_file_name', config, 'THCompetencyMaster.xlsx')
    ad.args.report_directory = str_arg(ad.args.report_directory, 'report_directory', config, current_directory)
    ad.args.report_password = str_arg(ad.args.report_password, 'report_password', config, 'Education2021')
    ad.args.readonly = bool_arg(ad.args.readonly, 'readonly', config)
    ad.args.supervisor = bool_arg(ad.args.supervisor, 'supervisor', config)
    ad.args.readonly = bool_arg(ad.args.readonly, 'readonly', config)
    ad.args.logging_level = list_arg(ad.args.logging_level, 'logging_level', config, log_levels, 'INFO', upper=True)
    ad.args.logging_directory = str_arg(ad.args.logging_directory, 'logging_directory', config, None)
    ad.args.logging_file_name = str_arg(ad.args.logging_file_name, 'logging_file_name', config, ad.app_name + '.log')
    ad.args.retention = int_arg(ad.args.retention, 'retention', config, 30)
    ad.args.theme = list_arg(ad.args.theme, 'theme', config, themes, 'green', lower=True)
    ad.args.icon = str_arg(ad.args.icon, 'icon', config, 'Th.png')

    # Ensure the logging directory is writeable
    if not ad.args.logging_directory or not os.access(ad.args.logging_directory, os.W_OK):
        if os.access(ad.args.master_excel_directory, os.W_OK):
            ad.args.logging_directory = ad.args.master_excel_directory
        else:
            ad.args.logging_directory = app_directory

    setup_logger(ad)

    ad.app_version = get_version_number(app_path)
    logger.info(f"Running {ad.app_name} from directory {app_directory}")
    logger.info(f"version: {ad.app_version}")
    logger.info(f"User: {ad.username}")
    logger.info(f"Current directory: {current_directory}")
    logger.info(f"Arguments from argparse")
    for key in ad.args.__dict__:
        logger.info(f"    {key: <23}: {ad.args.__dict__[key]}")

    # Dictionary of configuration status reference data
    ad.status_dict = {
        0: {'description': "Out of Date", 'colour': '#FF0000', 'default': '#FF0000'},
        1: {'description': "FT Needed", 'colour': '#FFFF40', 'default': '#FFFF40'},
        2: {'description': "Competency Needed", 'colour': '#B7DEE8', 'default': '#B7DEE8'},
        3: {'description': "Next Three Months", 'colour': '#FCD5B4', 'default': '#FCD5B4'},
        4: {'description': "In Date", 'colour': '#D8E4BC', 'default': '#D8E4BC'},
        5: {'description': "Not Required", 'colour': '#D9D9D9', 'default': '#D9D9D9'},
        6: {'description': "Not Relevant", 'colour': '#FFFFFF', 'default': '#FFFFFF'}}

    # Apply saved colors from json configuration file
    ad.configuration_path = str(os.path.join(ad.args.master_excel_directory, f'{ad.app_name}.json'))
    read_json_configuration(ad)


def get_version_number(file_name: str) -> str:
    try:
        info = GetFileVersionInfo(file_name, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return f"{LOWORD(ms)}.{HIWORD(ls)}.{LOWORD(ls)}"
    except pywintypes.error:
        logger.warning(f"Fail to get version info for: {file_name}")
        return "0.0.0"


def resource(relative_path: str) -> str:
    """Add location of script or executable to a path."""
    # If running pyinstaller executable use executable location)
    if '_MEI' in __file__ or '_internal' in __file__:
        base_path = os.path.dirname(os.path.abspath(sys.executable))
    # If running a python script use script location
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    resource = str(os.path.join(base_path, relative_path))
    logger.debug(f"Resource returned {resource}")
    return resource


def read_json_configuration(ad: AppData) -> None:
    """Read configuration json file apply configuration changes. At present
       this is only the colours used for competency statuses."""
    if not os.path.isfile(ad.configuration_path):
        logger.info(f"json configuration file does not exist path {ad.configuration_path}")
        return

    logger.info(f"Reading json configuration file {ad.configuration_path}")
    with open(ad.configuration_path) as jfile:
        configuration_json = json.load(jfile)

    try:
        ad.status_dict[0]['colour'] = configuration_json['out_of_date']
        ad.status_dict[1]['colour'] = configuration_json['ft_needed']
        ad.status_dict[2]['colour'] = configuration_json['comp_needed']
        ad.status_dict[3]['colour'] = configuration_json['next_3_months']
        ad.status_dict[4]['colour'] = configuration_json['in_date']
        ad.status_dict[5]['colour'] = configuration_json['not_required']
        ad.status_dict[6]['colour'] = configuration_json['not_relevant']
    except KeyError as e:
        logger.warning(f"json configuration file key error {e}")


def write_json_configuration(ad: AppData) -> None:
    """Write configuration json file to store configuration changes. At present
       this is only the colours used for competency statuses."""
    configuration = {
        'out_of_date': ad.status_dict[0]['colour'],
        'ft_needed': ad.status_dict[1]['colour'],
        'comp_needed': ad.status_dict[2]['colour'],
        'next_3_months': ad.status_dict[3]['colour'],
        'in_date': ad.status_dict[4]['colour'],
        'not_required': ad.status_dict[5]['colour'],
        'not_relevant': ad.status_dict[6]['colour']}
    configuration_json = json.loads(json.dumps(configuration))

    logger.info(f"Writing json configuration file {ad.configuration_path}")

    with open(ad.configuration_path, 'w') as jfile:
        json.dump(configuration_json, jfile, indent=4)
