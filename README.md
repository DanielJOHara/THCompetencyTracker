# TH Competency Tracker

TH Competency Tracker is a desktop application designed to maintain a record of staff competencies. It tracks achieved competencies and role requirements, storing its data in a master Excel spreadsheet and producing various Excel reports.

## Features

*   **Competency Grid**: A user-friendly interface that mimics the spreadsheet format previously used for tracking.
*   **Reporting**: Generates three types of Excel reports:
    1.  A static export of the Competency Grid.
    2.  A Competency Report with a sheet for each competency, detailing the status for each staff member.
    3.  A Staff Report with a sheet for each staff member, detailing the status for each competency.

## Data Management

The application provides a "Data Management" window that allows for the maintenance of the master data tables. The following data management interfaces are available:

*   **Service Areas**: Manage the different service areas in the organization.
*   **Roles**: Define and update the roles within the organization.
*   **Staff**: Manage staff information.
*   **Competencies**: Define and update the list of competencies.
*   **Staff Roles**: Assign roles to staff members.
*   **Role Competencies**: Define the competencies required for each role.
*   **Colour Selector**: Customize the colors used in the application.

## Setup

To set up the project for development, follow these steps:

1.  **Prerequisites**: Ensure you have Python 3 installed on your system.

2.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd THCompetencyTracker
    ```

3.  **Create a virtual environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

4.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the application, execute the following command from the project's root directory:

```bash
python -m source.main
```

## Running Tests

To run the test suite, use `pytest`:

```bash
pytest
```