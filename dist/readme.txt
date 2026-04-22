Version 0.0.0.0
Initial release

Version 0.1.0.0
Technical Changes:
    Code refactored.
    Class implemented for master data to move towards decoupling data storager method.
    Classes implemented for tkinter windows to aid testing.
    Unit testing implementation started.
Functional Changes:
    Moved configuration file location to master data folder to make colour selection common for all users.

Version 0.1.1.0
Technical Changes:
    Logging defined in each file and logger removed from application data object.
Functional Changes:
    Report sheets protected with password.
    Out Standing Competencies column added to summary sheet of staff report.
    Header added to report sheets.

Version 0.1.1.0 (no version update)
Functional Changes:
    Simplified file access error messages for user.
    Added role information to staff update window.
    Changed Staff Role update window to display all roles for a staff member.
    Expired competencies that are not required are greyed out rather that red.

Version 0.1.2.0
Technical Changes:
    Forward slashes changed backslashes in all paths returned by tkinter.filedialog calls.
Functional Changes:
    Corrected configuration file name from app_name.json to THCompetencyTracker.json.
    Added staff document functionality.

Version 0.1.2.1
Technical Changes:
    File names aligned with content.
    File and path selection moved to windows classes rather than report functions.
Functional Changes:
    Trap template errors when producing Staff documents.
    Add buttons for Template File and Document Path Selection.

Version 0.1.2.2
Functional Changes:
    Template selection on Staff Document Select window corrected.
    Change Role Competency data maintenance to use a grid.

Version 0.1.2.3
Functional Changes:
    Added information window after all saves and add actions.

Version 0.1.2.4
Functional Changes:
    Add window to select service codes and staff types for grid export.

Version 0.1.2.5
Functional Changes:
    Made staff role window open when a staff member is added.

Version 0.1.2.6
Functional Changes:
    Added read only option.
    Added rollover text on Role Codes and Competency Names on the Role Competency and Staff Competency Grid windows.
    When reloading data check master data is not locked.

Version 0.1.2.7
Technical Changes:
    Refactored code and added tests using Gemini CLI.
Functional Changes:
    Added Practice Assessor and Supervisor to Competency Grid
    Added filters to Staff Update window
    Blank input fields after records added
    Automatically close Staff Role Update window when inputting data for a single staff member

Version 0.1.2.8
Functional Changes:
    Apply filters on Staff Update window after any change.
    On Competency Report only include competencies relevant to staff type selected.
    Capitalise Staff Name when adding new staff.

Version 0.1.2.9
Technical Changes:
    Resolved all detected formatting issues.
Functional Changes:
    Corrected Staff Name processing to put capitals after apostrophe.
    Filters applied automatically when enter is used on Staff Name, drop down option selected or check box clicked.
    Added a label at bottom of the main menu showing application name and version.
    Do not display Practice Supervisor field unless new -s option is selected.

Version 0.1.2.10
Technical Changes:
    Added command line parameters for theme colour and window icon

Version 0.1.2.11
Technical Changes:
    Reset modify date on archived master files so that it will be retained for the full retention period.
    Reviewed and completed type hints.
Functional Changes:
    Added automatic filtering to staff delete that was missed in last version.
    Made name filter automatically apply when leaving the entry field.
    Formated date fields in staff report.
    Added window to select service codes and staff types for staff report.
    Standardised Competency Report Select to be same as Grid Export and new Staff Report Select.
    Added protection without a password to the master data excel spreadsheet.
    Added an INI file to set parameters.
    Removed staff competency colours from the parameter.
    Corrected Service Update Window save functionality.
    Offer readonly option when master data is in use.

Version 0.1.2.12
Technical Changes:
    Additional DEBUG logging added.
    Decoupled master data error handling from GUI.
    Automatically add audit columns to tables if they are missing.
Functional Changes:
    Added Competency Service table and an update grid window for it to Data Management.
    Added Services column to Competency update window.
    Added Role Service table and an update grid window for it to Data Management.
    Added Services column to Role update window.
    On Competency Role update grid window filter Roles and Competencies using the two new tables.
    Fixed bug on Staff update grid, clicking Roles failed after filtering reduced then increased rows displayed.
    Stopped filtering numbers from sheet names in Competency and Staff reports.
    Corrected bug on Competency and Staff reports where competency status not visible for first row.
    Added Services column to Competency report Competency summary sheet.
    Added Competency Service to filtering on Competency and Staff reports.
