import pytest
from unittest.mock import MagicMock
from source.role_service_logic import RoleServiceLogic

@pytest.fixture
def rsl(ad):
    return RoleServiceLogic(ad)

def test_save_all_role_service(ad, rsl):
    # Setup mock checkboxes
    # conftest has 2 roles, 3 services
    num_roles = ad.md.len('Role')
    num_serv = ad.md.len('Service')
    
    chc_cs = []
    for r in range(num_roles):
        row = []
        for s in range(num_serv):
            mock_chc = MagicMock()
            # Initially, checkboxes should match existing data in conftest.py
            role_code = ad.md.get('Role', 'Role Code', r)
            serv_code = ad.md.get('Service', 'Service Code', s)
            if ad.md.find_two('Role Service', role_code, 'Role Code', serv_code, 'Service Code') > -1:
                mock_chc.get.return_value = 1
            else:
                mock_chc.get.return_value = 0
            row.append(mock_chc)
        chc_cs.append(row)
        
    # No changes
    changes = rsl.save_all_role_service(chc_cs)
    assert changes == 0
    
    # Add a change: Check a box that was unchecked
    # R1 (0) - SC2 (1) is NOT in Role Service in conftest
    chc_cs[0][1].get.return_value = 1
    changes = rsl.save_all_role_service(chc_cs)
    assert changes == 1
    assert ad.md.find_two('Role Service', 'R1', 'Role Code', 'SC2', 'Service Code') > -1
    
    # Remove a change: Uncheck a box that was checked
    # R1 (0) - SC1 (0) IS in Role Service
    chc_cs[0][0].get.return_value = 0
    changes = rsl.save_all_role_service(chc_cs)
    assert changes == 1
    assert ad.md.find_two('Role Service', 'R1', 'Role Code', 'SC1', 'Service Code') == -1

def test_reset_role_service(ad, rsl):
    num_roles = ad.md.len('Role')
    num_serv = ad.md.len('Service')
    
    chc_cs = []
    for r in range(num_roles):
        row = []
        for s in range(num_serv):
            mock_chc = MagicMock()
            # Set all to unchecked initially
            mock_chc.get.return_value = 0
            row.append(mock_chc)
        chc_cs.append(row)
        
    rsl.reset_role_service(chc_cs)
    
    # Verify checkboxes are selected if they are in the database
    # R1 - SC1 is in database
    assert chc_cs[0][0].select.called
    # R1 - SC2 is NOT in database
    assert not chc_cs[0][1].select.called

def test_save_role_service_single(ad, rsl):
    # Save services for a single role (e.g., R2)
    role_code = 'R2'
    num_serv = ad.md.len('Service')
    chc_services = []
    for s in range(num_serv):
        mock_chc = MagicMock()
        mock_chc.get.return_value = 0
        chc_services.append(mock_chc)
        
    # Check SC1 and SC3 for R2
    chc_services[0].get.return_value = 1
    chc_services[2].get.return_value = 1
    
    changes = rsl.save_role_service(role_code, chc_services)
    assert changes >= 1 # Depending on initial state of R2
    assert ad.md.find_two('Role Service', role_code, 'Role Code', 'SC1', 'Service Code') > -1
    assert ad.md.find_two('Role Service', role_code, 'Role Code', 'SC3', 'Service Code') > -1
