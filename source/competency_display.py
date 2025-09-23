"""This module contains the routines to process Competencies for competency grid and reports."""
import datetime
import logging
from dateutil.relativedelta import relativedelta
from typing import Union, Tuple

from source.appdata import AppData
from source.window import date_to_string

logger = logging.getLogger(__name__)


def staff_competency_lists(ad: AppData, service_code: str, staff_type: str) -> Tuple[list[int], list[int]]:
    """Generate list of Staff and Competency indexes needed to generate the staff competency grid
       or the staff competency Excel report for a Service Code and Staff Type combination."""
    # Create a list of the role code for RNs or HCAs
    rn_flg = staff_type == 'RN'
    role_code_lst = []
    for db_r in range(ad.md.len('Role')):
        if rn_flg and ad.md.get('Role', 'RN', db_r) or not rn_flg and not ad.md.get('Role', 'RN', db_r):
            role_code_lst.append(ad.md.get('Role', 'Role Code', db_r))
    logger.debug(f"Role list for {service_code} {staff_type}s: {role_code_lst}")

    # Create a list of Staff indexes in role order (bank staff at end)
    db_s_list = []
    # Split into bank and non-bank
    for bank in [0, 1]:
        # Split by role in order of roles in role table
        for role_code in role_code_lst:
            # Within role will be in order of Staff table which is alphabetic by name
            for db_s in range(ad.md.len('Staff')):
                # Find if staff member has a role in the service
                db_sr = ad.md.find_three('Staff Role',
                                         service_code, 'Service Code',
                                         ad.md.get('Staff', 'Staff Name', db_s), 'Staff Name',
                                         role_code, 'Role Code')
                if db_sr > -1:
                    # Add staff if the role is bank or non-bank depending which split we are working on
                    if ad.md.get('Staff Role', 'Bank', db_sr) == bank:
                        db_s_list.append(db_s)

    logger.debug(f"Staff index list for {service_code} {staff_type}s: {db_s_list}")

    # Create a list of Competency indexes for RN or HCA where the competency is
    # assigned to a role for the service dependent
    db_c_list = []
    for db_c in range(ad.md.len('Competency')):
        if (ad.md.get('Competency', 'Scope', db_c) in ['BOTH', staff_type]
                and ad.md.find_two('Role Competency',
                                   service_code, 'Service Code',
                                   ad.md.get('Competency', 'Competency Name', db_c), 'Competency Name') > -1):
            db_c_list.append(db_c)

    logger.debug(f"Competency index list for {service_code} {staff_type}s: {db_c_list}")

    return db_s_list, db_c_list


def set_display_value(ad: AppData, service_code: str, db_s: int, db_c: int) -> tuple[Union[str, datetime.date], str]:
    """Set the display value and colour for a staff and competency combination within a service."""
    staff_name = ad.md.get('Staff', 'Staff Name', db_s)
    competency_name = ad.md.get('Competency', 'Competency Name', db_c)

    db_sc = ad.md.find_two('Staff Competency',
                           staff_name, 'Staff Name',
                           competency_name, 'Competency Name')

    # Set display value
    if db_sc <= -1:
        display_value = ''
    elif ad.md.get('Staff Competency', 'Competency Date', db_sc):
        display_value = ad.md.get('Staff Competency', 'Competency Date', db_sc)
    elif ad.md.get('Staff Competency', 'Prerequisite Date', db_sc):
        display_value = 'FT ' + date_to_string(ad.md.get('Staff Competency', 'Prerequisite Date', db_sc))
    else:
        display_value = ad.md.get('Staff Competency', 'Notes', db_sc)

    # Set display colour
    status = set_competency_status(ad, db_s, db_c, [service_code])
    colour = ad.status_dict[status]['colour']

    return display_value, colour


def set_competency_status(ad: AppData, db_s: int, db_c: int, service_code_list: list[str]) -> int:
    """Set competency status;
           0-Out of Date,
           1-FT Needed,
           2-Competency Needed,
           3-Next Three Months,
           4-In Date,
           5-Not Required
           6-Not Relevant."""
    staff_name = ad.md.get('Staff', 'Staff Name', db_s)

    competency_name = ad.md.get('Competency', 'Competency Name', db_c)
    competency_nightshift = ad.md.get('Competency', 'Nightshift', db_c)
    competency_bank = ad.md.get('Competency', 'Bank', db_c)

    db_sc = ad.md.find_two('Staff Competency',
                           staff_name, 'Staff Name',
                           competency_name, 'Competency Name')

    db_sc_found = False
    required = False
    relevant = False
    for service_code in service_code_list:
        if db_sc > -1:
            db_sc_found = True

        db_sr = ad.md.find_two('Staff Role',
                               service_code, 'Service Code',
                               staff_name, 'Staff Name')
        if db_sr > -1:
            role_code = ad.md.get('Staff Role', 'Role Code', db_sr)
            staff_nightshift = ad.md.get('Staff Role', 'Nightshift', db_sr)
            staff_bank = ad.md.get('Staff Role', 'Bank', db_sr)
            db_r = ad.md.find_one('Role', role_code, 'Role Code')
            if ad.md.get('Role', 'RN', db_r):
                staff_type = 'RN'
            else:
                staff_type = 'HCA'
            db_rc = ad.md.find_three('Role Competency',
                                     service_code, 'Service Code',
                                     role_code, 'Role Code',
                                     competency_name, 'Competency Name')
        else:
            db_rc = -1
            staff_nightshift = None
            staff_bank = None
            staff_type = None

        # Competence is required if it is explicitly set as required or these are all true:
        # 1. It is required for the role for the service,
        # 2. Is not explicitly marked as not required for the staff member
        # 3. Is not excluded for nights when the staff member is night staff
        # 4. Is not excluded for bank when the staff member is bank staff
        if (db_sc > -1 and ad.md.get('Staff Competency', 'Required', db_sc)
            or (db_rc > -1
                and not (db_sc > -1 and ad.md.get('Staff Competency', 'Not Required', db_sc))
                and not (not competency_nightshift and staff_nightshift)
                and not (not competency_bank and staff_bank))):
            required = True

        # A competency is relevant if it relates to the staff type from the staff role
        # and is required for any Role for the Service
        scope = ad.md.get('Competency', 'Scope', db_c)
        if (db_sr > -1
            and (staff_type == scope or scope == 'BOTH')
            and ad.md.find_two('Role Competency',
                               service_code, 'Service Code',
                               competency_name, 'Competency Name') > -1):
            relevant = True

    # If there is no record for the staff member for the competency set it based on the competencies settings
    if not db_sc_found:
        if not relevant:
            return 6
        elif not required:
            return 5
        elif ad.md.get('Competency', 'Prerequisite', db_c):
            return 1
        else:
            return 2

    # If competency date is set check if it is in date
    elif isinstance(ad.md.get('Staff Competency', 'Competency Date', db_sc), datetime.date):
        # If competency does not expire it is in date
        if not ad.md.get('Competency', 'Expiry', db_c):
            return 4
        # Test if past expire date
        elif (ad.md.get('Staff Competency', 'Competency Date', db_sc)
              + relativedelta(months=ad.md.get('Competency', 'Expiry', db_c) * 12)
                < datetime.datetime.today().date()):
            if required:
                return 0
            else:
                return 5
        # Test if within 3 months of expiry date
        elif (ad.md.get('Staff Competency', 'Competency Date', db_sc)
              + relativedelta(months=ad.md.get('Competency', 'Expiry', db_c) * 12 - 3)
                < datetime.datetime.today().date()):
            return 3
        # It is in date
        else:
            return 4
    # Check if flagged as completed
    elif ad.md.get('Staff Competency', 'Completed', db_sc):
        return 4
    # Not completed but is it required
    elif not required:
        return 5
    # Test if competency has prerequisites and they are not achieved
    elif (ad.md.get('Competency', 'Prerequisite', db_c)
          and not isinstance(ad.md.get('Staff Competency', 'Prerequisite Date', db_sc), datetime.date)
          and not ad.md.get('Staff Competency', 'Achieved', db_sc)):
        return 1
    # Prerequisites are achieved or not required so we need competency
    else:
        return 2
