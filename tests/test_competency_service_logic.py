import pytest
from unittest.mock import MagicMock
from source.competency_service_logic import CompetencyServiceLogic

@pytest.fixture
def csl(ad):
    return CompetencyServiceLogic(ad)

def test_save_all_competency_service(ad, csl):
    # Setup mock checkboxes
    # conftest has 3 competencies, 3 services
    num_comp = ad.md.len('Competency')
    num_serv = ad.md.len('Service')
    
    chc_cs = []
    for c in range(num_comp):
        row = []
        for s in range(num_serv):
            mock_chc = MagicMock()
            # Initially, checkboxes should match existing data in conftest.py
            comp_name = ad.md.get('Competency', 'Competency Name', c)
            serv_code = ad.md.get('Service', 'Service Code', s)
            if ad.md.find_two('Competency Service', comp_name, 'Competency Name', serv_code, 'Service Code') > -1:
                mock_chc.get.return_value = 1
            else:
                mock_chc.get.return_value = 0
            row.append(mock_chc)
        chc_cs.append(row)
        
    # No changes
    changes = csl.save_all_competency_service(chc_cs)
    assert changes == 0
    
    # Add a change: Check a box that was unchecked
    # VoED (0) - SC3 (2) is NOT in Competency Service in conftest
    chc_cs[0][2].get.return_value = 1
    changes = csl.save_all_competency_service(chc_cs)
    assert changes == 1
    assert ad.md.find_two('Competency Service', 'VoED', 'Competency Name', 'SC3', 'Service Code') > -1
    
    # Remove a change: Uncheck a box that was checked
    # VoED (0) - SC1 (0) IS in Competency Service
    chc_cs[0][0].get.return_value = 0
    changes = csl.save_all_competency_service(chc_cs)
    assert changes == 1
    assert ad.md.find_two('Competency Service', 'VoED', 'Competency Name', 'SC1', 'Service Code') == -1

def test_reset_competency_service(ad, csl):
    num_comp = ad.md.len('Competency')
    num_serv = ad.md.len('Service')
    
    chc_cs = []
    for c in range(num_comp):
        row = []
        for s in range(num_serv):
            mock_chc = MagicMock()
            # Set all to unchecked initially
            mock_chc.get.return_value = 0
            row.append(mock_chc)
        chc_cs.append(row)
        
    csl.reset_competency_service(chc_cs)
    
    # Verify checkboxes are selected if they are in the database
    # VoED - SC1 is in database
    assert chc_cs[0][0].select.called
    # Phlebotomy - SC1 is NOT in database
    assert not chc_cs[2][0].select.called

def test_save_competency_service_single(ad, csl):
    # Save services for a single competency (e.g., Phlebotomy)
    comp_name = 'Phlebotomy'
    num_serv = ad.md.len('Service')
    chc_services = []
    for s in range(num_serv):
        mock_chc = MagicMock()
        mock_chc.get.return_value = 0
        chc_services.append(mock_chc)
        
    # Check SC1 and SC2 for Phlebotomy
    chc_services[0].get.return_value = 1
    chc_services[1].get.return_value = 1
    
    changes = csl.save_competency_service(comp_name, chc_services)
    assert changes == 2
    assert ad.md.find_two('Competency Service', comp_name, 'Competency Name', 'SC1', 'Service Code') > -1
    assert ad.md.find_two('Competency Service', comp_name, 'Competency Name', 'SC2', 'Service Code') > -1
