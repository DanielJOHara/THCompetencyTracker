from dataclasses import dataclass, field
from datetime import date


@dataclass
class Competency:
    """This dataclass holds a staff competency record."""
    staff_name: str
    competency_name: str
    competency_date: date


@dataclass
class CompetencyDifferences:
    """This dataclass holds a staff competency record."""
    missing_competency: list[str] = field(default_factory=list)
    extra_competency: list[str] = field(default_factory=list)
    missing_staff: list[str] = field(default_factory=list)
    extra_staff: list[str] = field(default_factory=list)
    missing_staff_comp: list[Competency] = field(default_factory=list)
    extra_staff_comp: list[Competency] = field(default_factory=list)
    staff_comp_date: list[Competency] = field(default_factory=list)
