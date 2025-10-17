
import os
import pytest
from unittest.mock import MagicMock
from source.master_data import MasterData
from source.appdata import AppData
from source.role_competency_logic import RoleCompetencyLogic


@pytest.fixture
def app_data(request):
    """Fixture to create an AppData object with a MasterData instance."""
    test_data_path = os.path.join(os.path.dirname(__file__), 'TestMasterData.xlsx')
    md = MasterData(test_data_path, 30)
    md.load()
    ad = AppData()
    ad.md = md

    def finalizer():
        md._unlock()

    request.addfinalizer(finalizer)
    return ad


@pytest.fixture
def role_competency_logic(app_data):
    """Fixture to create a RoleCompetencyLogic instance."""
    return RoleCompetencyLogic(app_data)


def test_get_competency_list(role_competency_logic):
    """Test getting a list of competencies for a given staff type."""
    rn_competencies = role_competency_logic.get_competency_list('RN')
    assert isinstance(rn_competencies, list)
    # Based on the test data, we expect to see competencies with scope 'RN' or 'BOTH'
    for db_c in rn_competencies:
        scope = role_competency_logic.ad.md.get('Competency', 'Scope', db_c)
        assert scope in ['RN', 'BOTH']


def test_get_role_list(role_competency_logic):
    """Test getting a list of roles for a given staff type."""
    rn_roles = role_competency_logic.get_role_list('RN')
    assert isinstance(rn_roles, list)
    # Based on the test data, we expect to see roles where RN is True
    for db_r in rn_roles:
        is_rn = role_competency_logic.ad.md.get('Role', 'RN', db_r)
        assert is_rn


def test_save_role_competencies(role_competency_logic):
    """Test saving the role competency grid."""
    service_code = 'IPS'
    db_c_list = [0]  # Assuming competency at index 0
    db_r_list = [0]  # Assuming role at index 0
    competency_name = role_competency_logic.ad.md.get('Competency', 'Competency Name', db_c_list[0])
    role_code = role_competency_logic.ad.md.get('Role', 'Role Code', db_r_list[0])

    # Mock checkbox widgets
    chc_rc = [[MagicMock()]]

    # Ensure the role competency does not exist initially
    db_rc = role_competency_logic.ad.md.find_three('Role Competency', service_code, 'Service Code', role_code, 'Role Code', competency_name, 'Competency Name')
    if db_rc > -1:
        role_competency_logic.ad.md.delete_row('Role Competency', db_rc)

    # Test adding a new role competency
    chc_rc[0][0].get.return_value = 1
    number_changes = role_competency_logic.save_role_competencies(service_code, db_c_list, db_r_list, chc_rc)
    assert number_changes == 1

    # Test deleting a role competency
    chc_rc[0][0].get.return_value = 0
    number_changes = role_competency_logic.save_role_competencies(service_code, db_c_list, db_r_list, chc_rc)
    assert number_changes == 1


def test_reset_role_competencies(role_competency_logic):
    """Test resetting the role competency grid."""
    service_code = 'IPS'
    db_c_list = [0]
    db_r_list = [0]
    competency_name = role_competency_logic.ad.md.get('Competency', 'Competency Name', db_c_list[0])
    role_code = role_competency_logic.ad.md.get('Role', 'Role Code', db_r_list[0])

    # Mock checkbox widgets
    chc_rc = [[MagicMock()]]

    # Ensure the role competency does not exist initially
    db_rc = role_competency_logic.ad.md.find_three('Role Competency', service_code, 'Service Code', role_code, 'Role Code', competency_name, 'Competency Name')
    if db_rc > -1:
        role_competency_logic.ad.md.delete_row('Role Competency', db_rc)

    # Case 1: Record does not exist, checkbox is checked -> should be deselected
    chc_rc[0][0].get.return_value = 1
    role_competency_logic.reset_role_competencies(service_code, db_c_list, db_r_list, chc_rc)
    chc_rc[0][0].deselect.assert_called_once()

    # Add the role competency for the next test case
    role_competency_logic.ad.md.add_row('Role Competency', {
        'Service Code': service_code,
        'Role Code': role_code,
        'Competency Name': competency_name
    })

    # Case 2: Record exists, checkbox is unchecked -> should be selected
    chc_rc[0][0].get.return_value = 0
    chc_rc[0][0].reset_mock()
    role_competency_logic.reset_role_competencies(service_code, db_c_list, db_r_list, chc_rc)
    chc_rc[0][0].select.assert_called_once()
