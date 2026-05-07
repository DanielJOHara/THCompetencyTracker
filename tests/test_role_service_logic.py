import pytest
from unittest.mock import MagicMock
from source.role_service_logic import RoleServiceLogic


@pytest.fixture
def rsl(ad):
    return RoleServiceLogic(ad)


def test_save_role_services(ad, rsl):
    # Setup values (2 roles, 3 services)
    num_roles = ad.md.len('Role')
    num_serv = ad.md.len('Service')
    
    value_rs = []
    for r in range(num_roles):
        row = []
        for s in range(num_serv):
            role_code = ad.md.get('Role', 'Role Code', r)
            serv_code = ad.md.get('Service', 'Service Code', s)
            if ad.md.find_two('Role Service', role_code, 'Role Code', serv_code, 'Service Code') > -1:
                row.append(1)
            else:
                row.append(0)
        value_rs.append(row)
        
    # No changes
    changes = rsl.save_role_services(value_rs)
    assert changes == 0
    
    # Add a change: Check a box that was unchecked
    # R1 (0) - SC2 (1) is NOT in Role Service in conftest
    value_rs[0][1] = 1
    changes = rsl.save_role_services(value_rs)
    assert changes == 1
    assert ad.md.find_two('Role Service', 'R1', 'Role Code', 'SC2', 'Service Code') > -1
    
    # Remove a change: Uncheck a box that was checked
    # R1 (0) - SC1 (0) IS in Role Service
    value_rs[0][0] = 0
    changes = rsl.save_role_services(value_rs)
    assert changes == 1
    assert ad.md.find_two('Role Service', 'R1', 'Role Code', 'SC1', 'Service Code') == -1


def test_save_role_service_single(ad, rsl):
    # Save services for a single role (e.g., R2)
    role_code = 'R2'
    num_serv = ad.md.len('Service')
    value_s = [0] * num_serv
        
    # Check SC1 and SC3 for R2
    value_s[0] = 1
    value_s[2] = 1
    
    changes = rsl.save_role_service(role_code, value_s)
    assert changes >= 1
    assert ad.md.find_two('Role Service', role_code, 'Role Code', 'SC1', 'Service Code') > -1
    assert ad.md.find_two('Role Service', role_code, 'Role Code', 'SC3', 'Service Code') > -1
