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
    Bank input fields after records added
    Automatically close Staff Role Update window when inputting data for a single staff member

Version 0.1.2.8
Functional Changes:
    Apply filters on Staff Update window after any change.
    On Competency Report only include competencies relevant to staff type selected.
    Capitalise Staff Name when adding new staff.

Version 0.1.2.9
Technical Changes:

Functional Changes:
    Corrected Staff Name processing to put capitals after apostrophe.
    Filters applied automatically when enter is used on Staff Name, drop down option selected or check box clicked.
