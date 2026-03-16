"""
The Competency Tracker provide a user interface to maintain a record of the competencies staff have
achieved and what is required for their role. It stores its data in a master Excel spreadsheet and
produces excel and word reports.

There are two ways to update competencies for staff members:
1.	Competency Grid: A window that presents the staff and their competencies in an interactive grid
    allowing the cells for a staff and competency combination to be clicked and update the status.
2.	Competency Update: A window allows the use to select staff competency combinations to be updated.

There are four reports that can be produced:
1.	Grid Export: An excel spreadsheet with a sheet containing a static version of the Staff Competency
    Grid for each Service Area and Staff Type combinations requested.
2.	Competency Report: An excel spreadsheet with a summary sheet for the competencies related to the
    Service Area and Staff Type combinations requested and a sheet for each competency giving the
    competency status for each staff members.
3.	Staff Report: An excel spreadsheet with a summary sheet for the staff members in the Service Area
    and Staff Type combinations requested and a sheet for each staff member giving the competency status
    for each competency.
4.	Staff Document: Word documents for the selected staff members giving the status for each relevant
    competency.

The application provides a "Data Management" window that allows for the maintenance of the master data
tables. The following data management interfaces are available:
1.	Service Areas: Manage the different service areas in the organization.
2.	Roles: Define and update the roles within the organization.
3.	Staff: Manage staff information.
4.	Competencies: Define and update the list of competencies.
5.	Staff Roles: Assign roles to staff members.
6.	Role Competencies: Define the competencies required for each role.
7.	Colour Selector: Customise the colours used in the application.

The tool only supports a single user at a time with update access. There is no limit on the number of users
with read only access.

"""
import sys
import logging

from source.appdata import AppData
from source.command_line import command_line, write_json_configuration
from source.root_window import RootWindow

logger = logging.getLogger(__name__)


def main() -> None:
    """The main program sets up the master database object and starts the root
       GUI window."""
    # Create master data object, this will hold data frame and application parameters
    ad = AppData()

    # Load command line options and start logger
    command_line(ad, __doc__)

    # Start GUI
    RootWindow(ad)

    # Write configuration json file
    if not ad.args.readonly:
        write_json_configuration(ad)

    logger.info("Exiting application")


if __name__ == '__main__':
    sys.exit(main())
