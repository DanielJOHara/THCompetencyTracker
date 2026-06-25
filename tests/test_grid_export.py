import os
import pandas as pd
from source.staff_competency_grid_export import competency_grid_export


def test_grid_export_creation(ad_with_status, tmp_path):
    report_path = os.path.join(tmp_path, "grid_export.xlsx")
    service_code_list = ["SC1"]
    staff_type_list = ["RN"]
    
    competency_grid_export(ad_with_status, report_path, service_code_list, staff_type_list)
    
    assert os.path.exists(report_path)
    # The sheet name should be "SC1 RNs"
    df = pd.read_excel(report_path, sheet_name='SC1 RNs', header=0)
    
    # Check headers
    assert 'Staff Name' in df.columns
    assert 'Job Role' in df.columns
    
    # Check staff member
    assert "John Doe" in df['Staff Name'].values
