import pytest
import logging

from source.competency_logic import CompetencyLogic
from source.master_data import MasterData
from source.appdata import AppData

# Set up logging
logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


@pytest.fixture
def ad(request):
    """Fixture to create an AppData object with a MasterData instance."""
    ad = AppData()
    ad.md = MasterData('None', 30)
    ad.md.add_table('Competency',
                    ['Competency Name', 'Display Order', 'Scope', 'Expiry', 'Prerequisite', 'Nightshift', 'Bank'],
                    [["VoED", 1, "BOTH", 2, 0, 0, 0],
                     ["Cannulation", 2, "RN", 0, 0, 0, 0],
                     ["Phlebotomy", 3, "HCA", 2, 0, 0, 0]])
    ad.md.add_table('Role Competency',
                    ['Service Code', 'Role Code', 'Competency Name'],
                    [["IPS", "SN", "VoED"]])
    ad.md.add_table('Staff Competency',
                    ['Staff Name', 'Competency Name'],
                    [["John Doe", "VoED"]])
    yield ad


@pytest.fixture
def competency_values(ad):
    competency_values = []
    for db_c in range(ad.md.len('Competency')):
        competency_values.append({'Competency Name': ad.md.get('Competency', 'Competency Name', db_c),
                                  'Display Order': str(ad.md.get('Competency', 'Display Order', db_c)),
                                  'Scope': ad.md.get('Competency', 'Scope', db_c),
                                  'Expiry': str(ad.md.get('Competency', 'Expiry', db_c)),
                                  'Prerequisite': ad.md.get('Competency', 'Prerequisite', db_c),
                                  'Nightshift': ad.md.get('Competency', 'Nightshift', db_c),
                                  'Bank': ad.md.get('Competency', 'Bank', db_c)})
    yield competency_values


def test_add_competency(ad):
    """Tests adding a new competency."""
    len_competency = ad.md.len('Competency')
    competency_name = "New Competency"
    scope = 'RN' 
    display_order = '1'
    expiry = '1'
    prerequisite = 1
    nightshift = 1
    bank = 1
    success, message = CompetencyLogic(ad).add_competency(competency_name, scope, display_order,
                                                          expiry, prerequisite, nightshift, bank)
    assert success is True
    assert message == f"Added {competency_name}"
    assert ad.md.len('Competency') == len_competency + 1
    assert ad.md.count('Competency', 'Competency Name', competency_name) == 1


def test_add_competency_blank_competency(ad):
    """Tests adding a blank competency."""
    len_competency = ad.md.len('Competency')
    competency_name = ""
    scope = 'RN'
    display_order = '1'
    expiry = '1'
    prerequisite = 1
    nightshift = 1
    bank = 1
    success, message = CompetencyLogic(ad).add_competency(competency_name, scope, display_order,
                                                          expiry, prerequisite, nightshift, bank)
    assert success is False
    assert message == "Competency Name field must be set!"
    assert ad.md.len('Competency') == len_competency


def test_add_competency_invalid_order(ad):
    """Tests adding a blank competency."""
    len_competency = ad.md.len('Competency')
    competency_name = "New Competency"
    scope = 'RN'
    display_order = 'X'
    expiry = '1'
    prerequisite = 1
    nightshift = 1
    bank = 1
    success, message = CompetencyLogic(ad).add_competency(competency_name, scope, display_order,
                                                          expiry, prerequisite, nightshift, bank)
    assert success is False
    assert message == "Display Order field must be an integer!"
    assert ad.md.len('Competency') == len_competency


def test_add_competency_invalid_expiry(ad):
    """Tests adding a blank competency."""
    len_competency = ad.md.len('Competency')
    competency_name = "New Competency"
    scope = 'RN'
    display_order = ''
    expiry = 'X'
    prerequisite = 1
    nightshift = 1
    bank = 1
    success, message = CompetencyLogic(ad).add_competency(competency_name, scope, display_order,
                                                          expiry, prerequisite, nightshift, bank)
    assert success is False
    assert message == "Expiry field must be blank or an integer!"
    assert ad.md.len('Competency') == len_competency


def test_update_competency_success(ad, competency_values):
    """Tests updating an existing competency."""
    old_competency_name = competency_values[0]['Competency Name']
    new_competency_name = old_competency_name + " New"
    competency_values[0]['Competency Name'] = new_competency_name
    input_valid, number_changes, message = CompetencyLogic(ad).save_competencies(competency_values)

    assert input_valid is True
    assert number_changes == 1
    assert message == f"{number_changes} changes saved"
    assert ad.md.count('Role Competency', 'Competency Name', old_competency_name) == 0
    assert ad.md.count('Role Competency', 'Competency Name', new_competency_name) == 1
    assert ad.md.count('Staff Competency', 'Competency Name', old_competency_name) == 0
    assert ad.md.count('Staff Competency', 'Competency Name', new_competency_name) == 1


def test_save_competency_no_changes(ad, competency_values):
    """Tests updating with no changes ."""
    input_valid, number_changes, message = CompetencyLogic(ad).save_competencies(competency_values)

    assert input_valid is True
    assert number_changes == 0
    assert message == f"{number_changes} changes saved"


def test_save_competency_invalid_order(ad, competency_values):
    """Tests updating a competency with invalid display order."""
    competency_values[0]['Display Order'] = 'X'
    input_valid, number_changes, message = CompetencyLogic(ad).save_competencies(competency_values)

    assert input_valid is False
    assert number_changes == 0
    assert message == "Display Order field must be integer!"


def test_save_competency_invalid_expiry(ad, competency_values):
    """Tests updating a competency with an invalid expiry."""
    competency_values[0]['Expiry'] = 'X'
    input_valid, number_changes, message = CompetencyLogic(ad).save_competencies(competency_values)

    assert input_valid is False
    assert number_changes == 0
    assert message == "Expiry field must be integer or blank!"


def test_delete_competency_existing(ad):
    """Tests deleting an existing competency without dependencies."""
    len_competency = ad.md.len('Competency')
    competency_name = ad.md.get('Competency', 'Competency Name', 1)
    success, warning, message = CompetencyLogic(ad).delete_competency(competency_name)

    assert success is True
    assert warning is False
    assert message == f"{competency_name} deleted."
    assert ad.md.len('Competency') == len_competency - 1
    assert ad.md.count('Competency', 'Competency Name', competency_name) == 0


def test_delete_competency_blank(ad):
    """Tests deleting a blank competency."""
    success, warning, message = CompetencyLogic(ad).delete_competency("")

    assert success is False
    assert warning is False
    assert message == "No competency selected."


def test_delete_competency_with_dependencies_warning(ad):
    """Tests deleting a competency with dependencies generates a warning."""
    len_competency = ad.md.len('Competency')
    competency_name = ad.md.get('Competency', 'Competency Name', 0)
    success, warning, message = CompetencyLogic(ad).delete_competency(competency_name)

    assert success is False
    assert warning is True
    assert (message
            == f"{competency_name} is used 1 times in Role Competency and 1 times in Staff Competency")
    assert ad.md.len('Competency') == len_competency
    assert ad.md.count('Competency', 'Competency Name', competency_name) == 1


def test_delete_competency_with_dependencies(ad):
    """Tests deleting a competency with dependencies."""
    len_competency = ad.md.len('Competency')
    competency_name = ad.md.get('Competency', 'Competency Name', 0)
    CompetencyLogic(ad).delete_competency_with_dependents(competency_name)

    assert ad.md.len('Competency') == len_competency - 1
    assert ad.md.count('Competency', 'Competency Name', competency_name) == 0
