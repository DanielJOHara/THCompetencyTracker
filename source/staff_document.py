"""This module generates a document for a list of staff members showing competency statuses.
   It uses a template word document."""
import datetime
import logging
import os
import subprocess
from typing import Any

from CTkMessagebox import CTkMessagebox
from docxtpl import DocxTemplate
from docx.opc.exceptions import PackageNotFoundError
from jinja2.exceptions import TemplateError

from source.appdata import AppData
from source.competency_display import set_competency_status

logger = logging.getLogger(__name__)


def staff_document(ad: AppData,
                   staff_name_list: list[str],
                   template_path: str,
                   document_directory: str) -> None:
    """Generate a document for a list of staff members showing competency statuses.
       It uses a template word document."""
    logger.info(f"Creating Staff Document(s) for {staff_name_list} from {template_path} in {document_directory}")

    template = DocxTemplate(template_path)

    for staff_name in staff_name_list:
        logger.info(f"Generating staff document for staff member >{staff_name}<")
        # Create role string of service area role combinations, most staff members will only have one
        role_code_txt = ''
        for service_code in ad.md.get_list('Service', 'Service Code'):
            db_sr = ad.md.find_two('Staff Role',
                                   service_code, 'Service Code',
                                   staff_name, 'Staff Name')
            if db_sr > -1:
                role_code_txt += f'{service_code} {ad.md.get('Staff Role', 'Role Code', db_sr)}, '

        # Create content dictionary
        content: dict[str, str | list[dict[str, str]]] = \
            {'StaffName': staff_name,
             'Role': role_code_txt[:-2],
             'Date': f'{datetime.date.today():%d %B %Y}'}

        # Add a blank list to hold competencies to content dictionary for each competency status
        for status in ad.status_dict:
            status_variable = ad.status_dict[status]['description'].replace(' ', '')
            content.update({status_variable: list[dict]})

        # Add competencies to appropriate status list for staff member
        db_s = ad.md.index('Staff', 'Staff Name', staff_name)
        for db_c in range(ad.md.len('Competency')):
            competency_name = ad.md.get('Competency', 'Competency Name', db_c)
            db_sc = ad.md.find_two('Staff Competency', staff_name, 'Staff Name', competency_name, 'Competency Name')
            if db_sc > -1:
                competency_date = ad.md.get('Staff Competency', 'Competency Date', db_sc)
                notes = ad.md.get('Staff Competency', 'Notes', db_c)
            else:
                competency_date = ''
                notes = ''
            status = set_competency_status(ad, db_s, db_c, ad.md.get_list('Service', 'Service Code'))
            status_variable = ad.status_dict[status]['description'].replace(' ', '')
            content[status_variable].append({'CompetencyName': competency_name,
                                             'CompetencyDate': competency_date,
                                             'CompetencyNotes': notes})

        # Add content to template
        try:
            template.render(content)
        except PackageNotFoundError as e:
            logger.warning(f"Error rendering template for {staff_name}: {e}")
            CTkMessagebox(title="Document Generation Error",
                          message='Check the template document is not open in Word', icon='warning')
            return
        except TemplateError as e:
            logger.warning(f"Error rendering template for {staff_name}: {e}")
            CTkMessagebox(title="Syntax Error in Template Document",
                          message=f'{e}', icon='warning')
            return

        # Save staff members document
        document_path = os.path.join(document_directory, f'{staff_name}.docx')
        try:
            template.save(document_path)
        except IOError as e:
            logger.warning(f"Error writing document for {staff_name}: {e}")
            CTkMessagebox(title=f"Check {staff_name}.docx Document is not open",
                          message=f'{e}', icon='warning')

    subprocess.Popen(f'explorer "{document_directory}"')
