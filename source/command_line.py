""" Module processes command line options for TH Competency Tracker and set up logging. This
    module also provides routines to write and read a json configuration file and a routine to
    add path to executable/script directory."""
import argparse
import json
import logging
import os
import sys
import win32api
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
    else:
        app_path = os.path.abspath(__file__)

    app_directory = os.path.dirname(app_path)
    app_version = get_version_number(app_path)
    app_name = 'THCompetencyTracker'
    username = os.getlogin().lower()
    current_directory = os.getcwd()

    # Put doc string in help
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        '-md',
        '--master_excel_directory',
        help="Master Excel directory, default application location",
        default=app_directory)

    parser.add_argument(
        '-mf',
        '--master_excel_file_name',
        help="Master Excel file name, default THCompetencyMaster.xlsx",
        default='THCompetencyMaster.xlsx')

    parser.add_argument(
        '-r',
        '--report_directory',
        help="Directory to output reports, default current directory",
        default=current_directory)

    parser.add_argument(
        '-rp',
        '--report_password',
        help="Report password to remove sheet protection, default Education2021",
        default='Education2021')

    parser.add_argument(
        '-ro',
        '--readonly',
        action="store_true",
        help="Run application in read only mode")

    parser.add_argument(
        '-l',
        '--logging_level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Logging level",
        default='INFO')

    parser.add_argument(
        '-ld',
        '--logging_directory',
        help="Logging file directory, default Master Excel Directory")

    parser.add_argument(
        '-lf',
        '--logging_file_name',
        help=f"Logging file name, default {app_name}.log",
        default=app_name + '.log')

    parser.add_argument(
        '-re',
        '--retention',
        type=int,
        help=f"Retention period for archive Master Excel files, default 30 days",
        default=30)

    parser.add_argument(
        '-cod',
        '--out_of_date',
        help="Out of date Colour",
        default='#FF0000')

    parser.add_argument(
        '-cft',
        '--ft_needed',
        help="FT Needed Colour",
        default='#FFFF40')

    parser.add_argument(
        '-ccn',
        '--comp_needed',
        help="Comp Needed Colour",
        default='#B7DEE8')

    parser.add_argument(
        '-cn3',
        '--next_3_months',
        help="Next 3 Months Colour",
        default='#FCD5B4')

    parser.add_argument(
        '-cid',
        '--in_date',
        help="In Date Colour",
        default='#D8E4BC')

    parser.add_argument(
        '-cnrq',
        '--not_required',
        help="Competency Not Required Colour",
        default='#D9D9D9')

    parser.add_argument(
        '-cnrv',
        '--not_relevant',
        help="Competency Not Relevant Colour",
        default='#FFFFFF')

    ad.args = parser.parse_args()

    ad.configuration_path = str(os.path.join(ad.args.master_excel_directory, f'{app_name}.json'))

    if not ad.args.logging_directory or not os.access(ad.args.logging_directory, os.W_OK):
        if os.access(ad.args.master_excel_directory, os.W_OK):
            ad.args.logging_directory = ad.args.master_excel_directory
        else:
            ad.args.logging_directory = app_directory

    setup_logger(ad)

    logger.info(f"Running {app_name} from directory {app_directory} version {app_version}"
                f" for {username} with current directory {current_directory}")
    logger.info(f"Arguments from argparse")
    for key in ad.args.__dict__:
        logger.info(f"    {key: <23}: {ad.args.__dict__[key]}")

    # Dictionary of configuration status reference data
    ad.status_dict = {
        0: {'description': "Out of Date", 'colour': ad.args.out_of_date, 'default': ad.args.out_of_date},
        1: {'description': "FT Needed", 'colour': ad.args.ft_needed, 'default': ad.args.ft_needed},
        2: {'description': "Competency Needed", 'colour': ad.args.comp_needed, 'default': ad.args.comp_needed},
        3: {'description': "Next Three Months", 'colour': ad.args.next_3_months, 'default': ad.args.next_3_months},
        4: {'description': "In Date", 'colour': ad.args.in_date, 'default': ad.args.in_date},
        5: {'description': "Not Required", 'colour': ad.args.not_required, 'default': ad.args.not_required},
        6: {'description': "Not Relevant", 'colour': ad.args.not_relevant, 'default': ad.args.not_relevant}}

    read_json_configuration(ad)


def get_version_number(filename):
    try:
        info = GetFileVersionInfo(filename, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls)
    except win32api.error:
        return 0, 0, 0, 0


def resource(relative_path: str) -> str:
    """Add location of script or executable to a path."""
    # If running pyinstaller executable use executable location)
    if '_MEI' in __file__ or '_internal' in __file__:
        base_path = os.path.dirname(os.path.abspath(sys.executable))
    # If running a python script use script location
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return str(os.path.join(base_path, relative_path))


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
