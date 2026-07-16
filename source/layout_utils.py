"""This module defines the LayoutUtils helper functions for UI widget layouts."""
import re
from typing import Optional, Tuple


class LayoutUtils:
    @staticmethod
    def parse_widget_label_num(widget_name: str, pattern: str = r'ctklabel(\d+)?') -> Optional[int]:
        """Parse the integer label number from a widget's name based on a regex pattern."""
        match = re.search(pattern, widget_name)
        if not match:
            return None
        if match.lastindex is not None and match.group(1) is not None:
            return int(match.group(1))
        return 1

    @staticmethod
    def grid_coords_from_label_num(label_num: int, columns_count: int) -> Tuple[int, int]:
        """Convert a 1-indexed sequential label number into 0-indexed (row, col) grid coordinates."""
        return (label_num - 1) // columns_count, (label_num - 1) % columns_count

    @staticmethod
    def assessor_row_from_label_num(label_num: int, staff_count: int) -> int:
        """Calculate the row index in the staff list from the widget label number,
        handling the wrap-around logic of the original formula."""
        return int((label_num % (2 * staff_count) + 1) / 2) - 1
