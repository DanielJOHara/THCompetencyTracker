import os
import pytest
import pandas as pd
from source.staff_report import staff_report


def test_staff_report_creation(ad_with_status, tmp_path):
    report_path = os.path.join(tmp_path, "staff_report.xlsx")
    service_code_list = ["SC1"]
    staff_type_list = ["RN"]
    
    # Run the report generation
    staff_report(ad_with_status, report_path, service_code_list, staff_type_list)
    
    # Verify file exists
    assert os.path.exists(report_path)
    
    # Check content using pandas (reading the first sheet 'Staff')
    df_sum = pd.read_excel(report_path, sheet_name='Staff')
    
    # Verify headers are present
    assert 'Staff Name' in df_sum.columns
    assert 'Out Standing Competencies' in df_sum.columns
    
    # Verify expected staff member is in the report
    assert "John Doe" in df_sum['Staff Name'].values
    assert "Jane Smith" not in df_sum['Staff Name'].values


def test_staff_report_multiple_filters(ad_with_status, tmp_path):
    report_path = os.path.join(tmp_path, "staff_report_multi.xlsx")
    
    # Include both RN and HCA, and both services
    staff_report(ad_with_status, report_path, ["SC1", "SC2"], ["RN", "HCA"])
    
    assert os.path.exists(report_path)
    df_sum = pd.read_excel(report_path, sheet_name='Staff')
    
    # Both John Doe and Jane Smith should be here now
    names = df_sum['Staff Name'].values
    assert "John Doe" in names
    assert "Jane Smith" in names
