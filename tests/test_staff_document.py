import os
import pytest
from unittest.mock import patch, MagicMock
from source.staff_document import staff_document


@pytest.fixture
def ad_with_status(ad):
    ad.status_dict = {
        0: {'title': "Out of Date", 'colour': '#FF0000', 'default': '#FF0000'},
        1: {'title': "FT Needed", 'colour': '#FFFF40', 'default': '#FFFF40'},
        2: {'title': "Competency Needed", 'colour': '#B7DEE8', 'default': '#B7DEE8'},
        3: {'title': "Next Three Months", 'colour': '#FCD5B4', 'default': '#FCD5B4'},
        4: {'title': "In Date", 'colour': '#D8E4BC', 'default': '#D8E4BC'},
        5: {'title': "Not Required", 'colour': '#D9D9D9', 'default': '#D9D9D9'},
        6: {'title': "Not Relevant", 'colour': '#FFFFFF', 'default': '#FFFFFF'}}
    return ad


@patch('source.staff_document.DocxTemplate')
@patch('source.staff_document.subprocess.Popen')
def test_staff_document_rendering(mock_popen, mock_docx, ad_with_status, tmp_path):
    mock_template = MagicMock()
    mock_docx.return_value = mock_template
    
    staff_names = ["John Doe"]
    template_path = "dummy_template.docx"
    output_dir = str(tmp_path)
    
    staff_document(ad_with_status, staff_names, template_path, output_dir)
    
    # Verify DocxTemplate was initialized with the correct path
    mock_docx.assert_called_once_with(template_path)
    
    # Verify template.render was called
    assert mock_template.render.called
    
    # Inspect the content passed to render
    render_content = mock_template.render.call_args[0][0]
    assert render_content['StaffName'] == "John Doe"
    assert 'Role' in render_content
    assert 'Date' in render_content
    
    # Verify status-based lists are present in content
    # Status titles from ad_with_status (e.g., "Out of Date" -> "OutofDate")
    for status in ad_with_status.status_dict.values():
        status_var = status['title'].replace(' ', '')
        assert status_var in render_content
        assert isinstance(render_content[status_var], list)

    # Verify template.save was called with correct path
    expected_save_path = os.path.join(output_dir, "John Doe.docx")
    mock_template.save.assert_called_once_with(expected_save_path)
    
    # Verify explorer was opened
    mock_popen.assert_called_once()


@patch('source.staff_document.DocxTemplate')
@patch('source.staff_document.subprocess.Popen')
@patch('source.staff_document.CTkMessagebox')
def test_staff_document_missing_template(mock_msgbox, mock_popen, mock_docx, ad_with_status, tmp_path):
    # Simulate PackageNotFoundError (e.g. file not found or not a docx)
    from docx.opc.exceptions import PackageNotFoundError
    mock_docx.side_effect = PackageNotFoundError("File not found")
    
    with pytest.raises(PackageNotFoundError): # It's raised during initialization in staff_document? 
        # Actually, looking at code:
        # template = DocxTemplate(template_path) <- this might raise it
        staff_document(ad_with_status, ["John Doe"], "non_existent.docx", str(tmp_path))


@patch('source.staff_document.DocxTemplate')
@patch('source.staff_document.subprocess.Popen')
def test_staff_document_multiple_staff(mock_popen, mock_docx, ad_with_status, tmp_path):
    mock_template = MagicMock()
    mock_docx.return_value = mock_template
    
    staff_names = ["John Doe", "Jane Smith"]
    staff_document(ad_with_status, staff_names, "template.docx", str(tmp_path))
    
    assert mock_template.render.call_count == 2
    assert mock_template.save.call_count == 2
