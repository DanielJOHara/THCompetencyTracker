import pytest
from unittest.mock import patch, MagicMock
import customtkinter as ctk
import _tkinter
import os
from source.competency_tracking import CompetencyTracking, StaffCompetencyGridSelect, ReportSelect, StaffDocumentSelect


def pump_events(wnd_root):
    while wnd_root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
        pass


@patch('source.competency_tracking.child_window')
def test_competency_tracking_menu(mock_child, ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    ad_with_status.args.readonly = False
    app = CompetencyTracking(ad_with_status, wnd)
    pump_events(ctk_root)
    
    app.btn_review.invoke()
    assert mock_child.called
    
    app.btn_input.invoke()
    assert mock_child.call_count == 2
    
    app.btn_grid.invoke()
    assert mock_child.call_count == 3
    
    wnd.destroy()
    pump_events(ctk_root)


@patch('source.competency_tracking.child_window')
def test_staff_competency_grid_select(mock_child, ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = StaffCompetencyGridSelect(ad_with_status, wnd)
    pump_events(ctk_root)
    
    app.cmb_service_code.set("SC1")
    app.cmb_staff_type.set("RN")
    app.call_review(None)
    
    mock_child.assert_called_once()
    # Check that window was destroyed after selection
    pump_events(ctk_root)


@pytest.mark.parametrize("report_type", ['GRID', 'COMPETENCY', 'STAFF'])
@patch('source.competency_tracking.tk.filedialog.asksaveasfilename')
def test_report_select_init(mock_save, report_type, ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = ReportSelect(ad_with_status, wnd, report_type)
    pump_events(ctk_root)
    
    assert app.report_title in wnd.title()
    assert len(app.chc_service_code_list) == ad_with_status.md.len('Service')
    
    wnd.destroy()
    pump_events(ctk_root)


@patch('source.competency_tracking.tk.filedialog.asksaveasfilename')
def test_report_select_generate(mock_save, ctk_root, ad_with_status):
    ad_with_status.args.report_directory = "C:\\temp"
    wnd = ctk.CTkToplevel(ctk_root)
    app = ReportSelect(ad_with_status, wnd, 'STAFF')
    pump_events(ctk_root)
    
    # Mock the report procedure to avoid real file ops
    app.report_procedure = MagicMock()
    
    # Select first service and RN
    app.chc_service_code_list[0].select()
    app.chc_rn.select()
    
    app.generate_report()
    assert app.report_procedure.called
    wnd.destroy()
    pump_events(ctk_root)


def test_staff_document_select_logic(ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = StaffDocumentSelect(ad_with_status, wnd)
    pump_events(ctk_root)
    
    # Test adding staff to list
    app.cmb_staff_name.set("John Doe")
    app.add_staff()
    assert "John Doe" in app.staff_list
    
    # Test removing staff
    app.remove_staff()
    assert "John Doe" not in app.staff_list
    
    # Test filter application
    app.ent_name_filter.insert(0, "Jane")
    app.apply_filters()
    # Verify combo values are filtered (Jane Smith should be there)
    assert "Jane Smith" in app.cmb_staff_name.cget("values")
    
    wnd.destroy()
    pump_events(ctk_root)


@patch('source.competency_tracking.staff_document')
def test_staff_document_generate(mock_doc, ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = StaffDocumentSelect(ad_with_status, wnd)
    app.staff_list = ["John Doe"]
    app.generate_documents()
    mock_doc.assert_called_once()
    assert app.staff_list == []
    wnd.destroy()
    pump_events(ctk_root)


@patch('source.competency_tracking.child_window')
def test_competency_tracking_readonly(mock_child, ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    ad_with_status.args.readonly = True
    ad_with_status.wnd_root = MagicMock()
    app = CompetencyTracking(ad_with_status, wnd)
    pump_events(ctk_root)
    
    # Buttons should not exist in readonly mode
    assert not hasattr(app, 'btn_review')
    assert not hasattr(app, 'btn_input')
    
    # Test on_closing in readonly mode
    app.on_closing()
    # ad_with_status.wnd_root.destroy should be called
    ad_with_status.wnd_root.destroy.assert_called()
    pump_events(ctk_root)


@patch('source.competency_tracking.input_warning')
def test_staff_competency_grid_select_invalid_font(mock_warning, ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = StaffCompetencyGridSelect(ad_with_status, wnd)
    
    app.ent_font_size.delete(0, 'end')
    app.ent_font_size.insert(0, "ABC")
    app.call_review(None)
    mock_warning.assert_called_with(wnd, "Font Size must be integer or blank!")
    wnd.destroy()
    pump_events(ctk_root)


@patch('source.competency_tracking.input_warning')
def test_report_select_validation(mock_warning, ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = ReportSelect(ad_with_status, wnd, 'GRID')
    
    # No selection
    app.generate_report()
    mock_warning.assert_called_with(wnd, "Check required Service Codes and Staff Types")
    
    # Only Service selected
    app.chc_service_code_list[0].select()
    app.generate_report()
    mock_warning.assert_called_with(wnd, "Check required Staff Types")
    
    # Only Staff Type selected
    app.chc_service_code_list[0].deselect()
    app.chc_rn.select()
    app.generate_report()
    mock_warning.assert_called_with(wnd, "Check required Service Codes")
    
    wnd.destroy()
    pump_events(ctk_root)


@patch('source.competency_tracking.tk.filedialog.askopenfilename', return_value='C:\\template.docx')
def test_staff_document_select_template(mock_file, ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = StaffDocumentSelect(ad_with_status, wnd)
    app.select_template()
    assert app.template_path == 'C:\\template.docx'
    wnd.destroy()
    pump_events(ctk_root)


@patch('source.competency_tracking.tk.filedialog.askdirectory', return_value='C:\\docs')
def test_staff_document_select_directory(mock_dir, ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = StaffDocumentSelect(ad_with_status, wnd)
    app.select_document_directory()
    assert app.document_directory == 'C:\\docs'
    wnd.destroy()
    pump_events(ctk_root)


@patch('source.competency_tracking.child_window')
def test_staff_competency_grid_select_empty_font(mock_child, ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = StaffCompetencyGridSelect(ad_with_status, wnd)
    app.ent_font_size.delete(0, 'end')
    app.cmb_service_code.set("SC1")
    app.cmb_staff_type.set("RN")
    app.call_review(None)
    mock_child.assert_called_once()
    wnd.destroy()
    pump_events(ctk_root)


@patch('source.competency_tracking.input_warning')
def test_report_select_invalid_type(mock_warning, ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    with patch('source.competency_tracking.logger') as mock_log:
        ReportSelect(ad_with_status, wnd, 'INVALID')
        mock_log.error.assert_called()
        assert mock_warning.called
    wnd.destroy()
    pump_events(ctk_root)


@patch('source.competency_tracking.tk.filedialog.asksaveasfilename', return_value='C:\\report.xlsx')
def test_report_select_file_select(mock_save, ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = ReportSelect(ad_with_status, wnd, 'GRID')
    app.file_select()
    assert app.report_path == 'C:\\report.xlsx'
    wnd.destroy()
    pump_events(ctk_root)


def test_staff_document_select_add_empty(ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = StaffDocumentSelect(ad_with_status, wnd)
    app.cmb_staff_name.set('')
    app.add_staff()
    assert len(app.staff_list) == 0
    wnd.destroy()
    pump_events(ctk_root)


def test_staff_document_select_filter_edge_cases(ctk_root, ad_with_status):
    wnd = ctk.CTkToplevel(ctk_root)
    app = StaffDocumentSelect(ad_with_status, wnd)
    
    # Filter with invalid characters in name
    app.ent_name_filter.insert(0, "John 123!")
    app.apply_filters()
    assert app.ent_name_filter.get() == "John"
    
    # Filter by role that is RN
    app.cmb_role_filter.set("R1")
    app.apply_filters()
    assert app.cmb_rn_filter.get() == "" # cmb_rn_filter doesn't change, but internal rn_filter does
    
    # Filter with no results
    app.ent_name_filter.delete(0, 'end')
    app.ent_name_filter.insert(0, "NonExistentStaff")
    app.apply_filters()
    assert app.cmb_staff_name.get() == ""
    
    wnd.destroy()
    pump_events(ctk_root)
