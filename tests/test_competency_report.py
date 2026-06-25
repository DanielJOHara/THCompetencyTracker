import os
import pandas as pd
from source.competency_report import competency_report


def test_competency_report_creation(ad_with_status, tmp_path):
    report_path = os.path.join(tmp_path, "competency_report.xlsx")
    service_code_list = ["SC1"]
    staff_type_list = ["RN"]
    
    competency_report(ad_with_status, report_path, service_code_list, staff_type_list)
    
    assert os.path.exists(report_path)
    df_sum = pd.read_excel(report_path, sheet_name='Competency')
    
    assert 'Competency Name' in df_sum.columns
    # VoED and Cannulation should be in SC1 for RN
    comp_names = df_sum['Competency Name'].values
    assert "VoED" in comp_names
    assert "Cannulation" in comp_names
    # Phlebotomy is HCA scope, should NOT be in RN report
    assert "Phlebotomy" not in comp_names


def test_competency_report_hca(ad_with_status, tmp_path):
    report_path = os.path.join(tmp_path, "competency_report_hca.xlsx")
    service_code_list = ["SC1"]
    staff_type_list = ["HCA"]
    
    competency_report(ad_with_status, report_path, service_code_list, staff_type_list)
    
    assert os.path.exists(report_path)
    df_sum = pd.read_excel(report_path, sheet_name='Competency')
    comp_names = df_sum['Competency Name'].values
    # Phlebotomy is NOT in SC1 (it's not in Competency Service table for SC1 in fixture)
    # Wait, let me check fixture again.
    # Competency Service: [["VoED", "SC1"], ["VoED", "SC2"], ["Cannulation", "SC1"]]
    # So Phlebotomy is indeed not in any service in the fixture.
    assert "Phlebotomy" not in comp_names
    assert "VoED" in comp_names # VoED is BOTH
