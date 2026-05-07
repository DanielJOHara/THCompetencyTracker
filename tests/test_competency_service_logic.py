import pytest
from unittest.mock import MagicMock
from source.competency_service_logic import CompetencyServiceLogic


@pytest.fixture
def csl(ad):
    return CompetencyServiceLogic(ad)


def test_save_competency_services(ad, csl):
    # Setup values
    # conftest has 3 competencies, 3 services
    num_comp = ad.md.len('Competency')
    num_serv = ad.md.len('Service')
    
    value_cs = []
    for c in range(num_comp):
        row = []
        for s in range(num_serv):
            comp_name = ad.md.get('Competency', 'Competency Name', c)
            serv_code = ad.md.get('Service', 'Service Code', s)
            if ad.md.find_two('Competency Service', comp_name, 'Competency Name', serv_code, 'Service Code') > -1:
                row.append(1)
            else:
                row.append(0)
        value_cs.append(row)
        
    # No changes
    changes = csl.save_competency_services(value_cs)
    assert changes == 0
    
    # Add a change: Check a box that was unchecked
    # Cannulation (1) - SC2 (1) is NOT in Competency Service in conftest
    value_cs[1][1] = 1
    changes = csl.save_competency_services(value_cs)
    assert changes == 1
    assert ad.md.find_two('Competency Service', 'Cannulation', 'Competency Name', 'SC2', 'Service Code') > -1
    
    # Remove a change: Uncheck a box that was checked
    # VoED (0) - SC1 (0) IS in Competency Service
    value_cs[0][0] = 0
    changes = csl.save_competency_services(value_cs)
    assert changes == 1
    assert ad.md.find_two('Competency Service', 'VoED', 'Competency Name', 'SC1', 'Service Code') == -1


def test_save_competency_service_single(ad, csl):
    # Save services for a single competency (e.g., Phlebotomy)
    comp_name = 'Phlebotomy'
    num_serv = ad.md.len('Service')
    value_s = [0] * num_serv
        
    # Check SC1 and SC2 for Phlebotomy
    value_s[0] = 1
    value_s[1] = 1
    
    changes = csl.save_competency_service(comp_name, value_s)
    assert changes == 2
    assert ad.md.find_two('Competency Service', comp_name, 'Competency Name', 'SC1', 'Service Code') > -1
    assert ad.md.find_two('Competency Service', comp_name, 'Competency Name', 'SC2', 'Service Code') > -1
