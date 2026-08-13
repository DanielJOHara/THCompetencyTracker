"""Function to read competency report file and compair it to the existing master data."""
import logging
import re
from datetime import datetime, date

import pandas as pd
import customtkinter as ctk

from appdata import AppData
from competency_differences import CompetencyDifferences, Competency
from window import staff_name_title_case, child_window, parse_date

logger = logging.getLogger(__name__)


def read_competency_report(ad: AppData, rep_df: pd.DataFrame, diff: CompetencyDifferences) -> None:
    """This function reads an competency status report in a dataframe and compares it to the
       master data. The differences are added to the supplied CompetencyDifferences data object."""

    # Add standard columns from the columns specified in the command line arguments
    # The Staff Name is either the concatenation of the First Name ad Surname or the Staff Name and 'fixed'
    # by removing ZZ at the start, reducing multiple spaces to a single space and set it to title case
    if ad.args.first_name_column:
        rep_df['Staff Name'] = rep_df.apply(
            lambda row: fix_staff_name(row[ad.args.first_name_column] + ' ' + row[ad.args.surname_column]), axis=1)
    else:
        rep_df['Staff Name'] = rep_df.apply(lambda row: fix_staff_name(row[ad.args.comp_staff_column]), axis=1)
        
    # Competency Name 'fixed' by removing any version number at the end and repacing
    # en dash character with a standard hyphen
    rep_df['Competency Name'] = rep_df.apply(lambda row: fix_competency_name(row[ad.args.comp_column]), axis=1)

    # Competency Date created from a datetime colum or a string that parses to a date
    if rep_df[ad.args.comp_date_column].dtype == 'datetime64[ns]':
        rep_df['Competency Date'] = rep_df.apply(lambda row: row[ad.args.comp_date_column].date(), axis=1)
    else:
        rep_df['Competency Date'] = rep_df.apply(lambda row: parse_date(row[ad.args.comp_date_column]), axis=1)

    # Generate a unique set of the competency name in the report
    rep_competency_set: set[str] = set(rep_df['Competency Name'])

    # Generate list of competency names associated with competency service area specified in a parameter
    service_competency_list: list[str] = []
    if ad.args.comp_service == 'ALL':
        service_competency_list = ad.md.get_list('Competency', 'Competency Name')
    else:
        db_cs: int = -1
        while True:
            db_cs = ad.md.find_one('Competency Service', ad.args.comp_service, 'Service Code', db_cs+1)
            if db_cs > -1:
                service_competency_list.append(ad.md.get('Competency Service', 'Competency Name', db_cs))
            else:
                break

    # Identify competency names in the report that are not in the master data
    for competency_name in rep_competency_set:
        if competency_name not in service_competency_list:
            logger.debug(f"{competency_name} from report NOT IN master data")
            diff.missing_competency.append(competency_name)

    # Identify competency names in the master data that are not in the report
    for competency_name in service_competency_list:
        if competency_name not in rep_competency_set:
            logger.debug(f"{competency_name} from master data NOT IN report")
            diff.extra_competency.append(competency_name)

    # Generate unique lists of staff names for all staff and only ex staff
    rep_staff_set: set[str] = set(rep_df['Staff Name'])

    # Generate a list of staff in competency report who have left, their name starts wit ZZ
    if ad.args.first_name_column:
        zz_mask = rep_df[ad.args.first_name_column].str.contains('^[Zz][Zz]')
    else:
        zz_mask = rep_df[ad.args.comp_staff_column].str.contains('^[Zz][Zz]')
    zz_staff = rep_df[zz_mask]
    zz_staff_set = set(zz_staff['Staff Name'])

    # Identify staff names in report that are not in the master data
    db_staff_list: list[str] = ad.md.get_list('Staff', 'Staff Name')
    for staff_name in rep_staff_set:
        if staff_name not in db_staff_list:
            logger.debug(f"{staff_name} from report NOT IN master data")
            diff.missing_staff.append(staff_name)

    # Identify staff names with staff competency record for competency service specified in the command line parameter
    service_staff_list: list[str] = []
    for staff_name in ad.md.get_list('Staff', 'Staff Name'):
        db_sc: int = -1
        while True:
            db_sc = ad.md.find_one('Staff Competency', staff_name, 'Staff Name', db_sc+1)
            if db_sc > -1:
                if ad.args.comp_service == 'ALL':
                    service_staff_list.append(staff_name)
                    break
                competency_name = ad.md.get('Staff Competency', 'Competency Name', db_sc)
                if ad.md.find_two('Competency Service',
                                  competency_name, 'Competency Name',
                                  ad.args.comp_service, 'Service Code') > -1:

                    service_staff_list.append(staff_name)
                    break
            else:
                break

    # Identify staff im master data not in report
    for staff_name in service_staff_list:
        if staff_name not in rep_staff_set:
            logger.debug(f"{staff_name} from master data NOT IN report")
            diff.extra_staff.append(staff_name)

    # Compair report entries to master data
    null_date: date = datetime.strptime('1999-01-01', '%Y-%m-%d').date()
    for i, row in rep_df.iterrows():
        staff_name: str = row['Staff Name']
        competency_name: str = row['Competency Name']
        rep_competency_date: date = row['Competency Date']

        db_sc = ad.md.find_two('Staff Competency',
                               staff_name, 'Staff Name',
                               competency_name, 'Competency Name')

        # Check for missing master data entries
        if db_sc == -1:
            if rep_competency_date != null_date:
                logger.debug(f"{staff_name}-{competency_name}-{rep_competency_date} not set in master data")
                diff.missing_staff_comp.append(Competency(staff_name, competency_name, rep_competency_date))
            continue

        db_competency_date = ad.md.get('Staff Competency', 'Competency Date', db_sc)
        db_completed = ad.md.get('Staff Competency', 'Completed', db_sc)

        # Check for place holder records in report
        if rep_competency_date == null_date:
            if db_completed or db_competency_date:
                logger.debug(f"{staff_name}-{competency_name}-{db_competency_date} has null date in report")
                diff.extra_staff_comp.append(Competency(staff_name, competency_name, db_competency_date))
            continue

        # Chek for missing records, ignore records for staff who have left
        if db_competency_date != rep_competency_date:
            if staff_name not in zz_staff_set:
                logger.debug(f"{staff_name}-{competency_name}-{rep_competency_date}"
                             f" has {db_competency_date} in master data")
                diff.staff_comp_date.append(Competency(staff_name, competency_name, rep_competency_date))

    # Check for master data staff competencies missing from the report
    for db_sc in range(ad.md.len('Staff Competency')):
        staff_name: str = ad.md.get('Staff Competency', 'Staff Name', db_sc)
        competency_name: str = ad.md.get('Staff Competency', 'Competency Name', db_sc)
        competency_date: date = ad.md.get('Staff Competency', 'Competency Date', db_sc)
        if competency_name not in service_competency_list:
            continue
        if len(rep_df[(rep_df['Staff Name'] == staff_name)
               & (rep_df['Competency Name'] == competency_name)].index) == 0:
            logger.debug(f"{staff_name}-{competency_name}-{competency_date} not in report")
            diff.extra_staff_comp.append(Competency(staff_name, competency_name, competency_date))

    diff.missing_competency.sort()
    diff.extra_competency.sort()
    diff.missing_staff.sort()
    diff.extra_staff.sort()
    diff.extra_competency.sort()
    diff.missing_staff_comp = sorted(diff.missing_staff_comp, key=lambda x: (x.staff_name, x.competency_name))
    diff.extra_staff_comp = sorted(diff.extra_staff_comp, key=lambda x: (x.staff_name, x.competency_name))
    diff.staff_comp_date = sorted(diff.staff_comp_date, key=lambda x: (x.staff_name, x.competency_name))

    logger.info(f"No missing competency names: {len(diff.missing_competency)}")
    logger.info(f"No extra competency names: {len(diff.extra_competency)}")
    logger.info(f"No missing staff names: {len(diff.missing_staff)}")
    logger.info(f"No extra staff names: {len(diff.extra_staff)}")
    logger.info(f"No missing competencies: {len(diff.missing_staff_comp)}")
    logger.info(f"No extra competencies: {len(diff.extra_staff_comp)}")
    logger.info(f"No competency date changes: {len(diff.staff_comp_date)}")


def fix_competency_name(competency_name: str) -> str:
    """Remove version ( V1) from the end of the competency names and replace the
       windows en dash (unicode 2013) characters with a standard hyphen."""
    competency_name = re.sub(r' *V\d+ *$', '', competency_name)
    competency_name = re.sub(u'\u2013', '-', competency_name)
    return competency_name


def fix_staff_name(staff_name: str) -> str:
    """Remove any ZZ from the star of the name and then standardises name using function used for user input."""
    staff_name = re.sub(r'^[Zz][Zz]', '', staff_name)
    staff_name = staff_name_title_case(staff_name)
    return staff_name
