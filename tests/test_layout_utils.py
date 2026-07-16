import pytest
from source.layout_utils import LayoutUtils


def test_parse_widget_label_num():
    # Test CTk widget name matching
    assert LayoutUtils.parse_widget_label_num(".!ctktoplevel.!ctkframe.!ctklabel3") == 3
    assert LayoutUtils.parse_widget_label_num(".!ctktoplevel.!ctkframe.!ctklabel") == 1
    
    # Test standard tkinter widget name matching with customized pattern
    assert LayoutUtils.parse_widget_label_num(".!ctktoplevel.!ctkframe.!label45", r'label(\d+)') == 45
    assert LayoutUtils.parse_widget_label_num(".!ctktoplevel.!ctkframe.!label", r'label(\d+)') is None
    
    # Test no match
    assert LayoutUtils.parse_widget_label_num("widget_name_without_label") is None


def test_grid_coords_from_label_num():
    # Columns count = 5
    # Label 1 (first row, first col) -> (0, 0)
    assert LayoutUtils.grid_coords_from_label_num(1, 5) == (0, 0)
    # Label 5 (first row, last col) -> (0, 4)
    assert LayoutUtils.grid_coords_from_label_num(5, 5) == (0, 4)
    # Label 6 (second row, first col) -> (1, 0)
    assert LayoutUtils.grid_coords_from_label_num(6, 5) == (1, 0)
    # Label 10 (second row, last col) -> (1, 4)
    assert LayoutUtils.grid_coords_from_label_num(10, 5) == (1, 4)
    # Label 11 (third row, first col) -> (2, 0)
    assert LayoutUtils.grid_coords_from_label_num(11, 5) == (2, 0)


def test_assessor_row_from_label_num():
    # Staff count = 5
    # label_num = 1 -> row 0
    assert LayoutUtils.assessor_row_from_label_num(1, 5) == 0
    # label_num = 2 -> row 0
    assert LayoutUtils.assessor_row_from_label_num(2, 5) == 0
    # label_num = 3 -> row 1
    assert LayoutUtils.assessor_row_from_label_num(3, 5) == 1
    # label_num = 9 -> row 4
    assert LayoutUtils.assessor_row_from_label_num(9, 5) == 4
    # label_num = 10 -> row -1 (wraps around early in original formula)
    assert LayoutUtils.assessor_row_from_label_num(10, 5) == -1
    # label_num = 11 -> row 0 (wrap around)
    assert LayoutUtils.assessor_row_from_label_num(11, 5) == 0
