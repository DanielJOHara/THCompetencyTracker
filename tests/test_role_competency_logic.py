import pytest
from source.role_competency_logic import RoleCompetencyLogic

@pytest.fixture
def rcl(ad):
    """Fixture to create a RoleCompetencyLogic instance."""
    return RoleCompetencyLogic(ad)


def test_get_role_list(rcl):
    """Test getting a list of roles for a given staff type."""
    rn_roles = rcl.get_role_list('RN')
    assert isinstance(rn_roles, list)
    # Based on the test data, we expect to see roles where RN is True
    for db_r in rn_roles:
        is_rn = rcl.ad.md.get('Role', 'RN', db_r)
        assert is_rn


def test_save_role_competencies(rcl):
    """Test saving the role competency grid."""
    service_code = 'SC1'
    db_c_list = [0]  # VoED
    db_r_list = [0]  # R1
    competency_name = rcl.ad.md.get('Competency', 'Competency Name', db_c_list[0])
    role_code = rcl.ad.md.get('Role', 'Role Code', db_r_list[0])

    # Ensure the role competency does not exist initially
    db_rc = rcl.ad.md.find_three('Role Competency',
                                 service_code, 'Service Code',
                                 role_code, 'Role Code',
                                 competency_name, 'Competency Name')
    if db_rc > -1:
        rcl.ad.md.delete_row('Role Competency', db_rc)

    # Test adding a new role competency
    value_rc = [[1]]
    number_changes = rcl.save_role_competencies(service_code, db_c_list, db_r_list, value_rc)
    assert number_changes == 1
    assert rcl.ad.md.find_three('Role Competency', service_code, 'Service Code', 
                                 role_code, 'Role Code', competency_name, 'Competency Name') > -1

    # Test deleting a role competency
    value_rc = [[0]]
    number_changes = rcl.save_role_competencies(service_code, db_c_list, db_r_list, value_rc)
    assert number_changes == 1
    assert rcl.ad.md.find_three('Role Competency', service_code, 'Service Code', 
                                 role_code, 'Role Code', competency_name, 'Competency Name') == -1
