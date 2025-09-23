"""
TH Competency Tracker provide a user interface to maintain a record of staff
competencies they have achieved and what is required for their role. It stores
its data in a master Excel spreadsheet and produces Excel reports. The
Competency Grid is a window in the format of the spreadsheet that was used to
track competencies before this tracker tool was introduced.

There are three spreadsheet reports that can be produced:

 1. A static version of the Grid can be exported.
 2. A Competency Report with a sheet for each competency giving the status for
    each member of staff.
 3. A Staff Report with a sheet for each member of staff giving the status for
    each competency.

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
