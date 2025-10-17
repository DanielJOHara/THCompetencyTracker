
import os
import pytest
from unittest.mock import MagicMock
from source.master_data import MasterData
from source.appdata import AppData
from source.competency_logic import CompetencyLogic


@pytest.fixture
def app_data():
    """Fixture to create an AppData object with a MasterData instance."""
    test_data_path = os.path.join(os.path.dirname(__file__), 'TestMasterData.xlsx')
    md = MasterData(test_data_path, 30)
    try:
        md.load()
        ad = AppData()
        ad.md = md
        yield ad
    finally:
        md._unlock()


@pytest.fixture
def competency_logic(app_data):
    """Fixture to create a CompetencyLogic instance."""
    return CompetencyLogic(app_data)


def test_add_competency(competency_logic):
    """Test adding a new competency."""
    competency_name = "New Competency"
    scope = "Test Scope"
    display_order = "10"
    expiry = "365"
    prerequisite = 0
    nightshift = 1
    bank = 0

    success, message = competency_logic.add_competency(
        competency_name, scope, display_order, expiry, prerequisite, nightshift, bank
    )

    assert success is True
    assert message == f"Added {competency_name}"
    assert competency_logic.ad.md.index('Competency', 'Competency Name', competency_name) is not None


def test_add_competency_existing(competency_logic):
    """Test adding a competency that already exists."""
    competency_name = "VoED"  # Existing competency
    scope = "Test Scope"
    display_order = "10"
    expiry = "365"
    prerequisite = 0
    nightshift = 1
    bank = 0

    success, message = competency_logic.add_competency(
        competency_name, scope, display_order, expiry, prerequisite, nightshift, bank
    )

    assert success is False
    assert message == f"Competency Name {competency_name} already defined!"


def test_delete_competency(competency_logic):
    """Test deleting a competency."""
    competency_name = "New Competency"
    competency_logic.add_competency(competency_name, "Test", "1", "365", 0, 0, 0)

    success, message = competency_logic.delete_competency(competency_name)

    assert success is True
    assert message == f"{competency_name} deleted."
    with pytest.raises(IndexError):
        competency_logic.ad.md.index('Competency', 'Competency Name', competency_name)


def test_delete_competency_with_dependents(competency_logic):
    """Test deleting a competency with dependent records."""
    competency_name = "VoED"  # Competency with dependents in test data

    success, message = competency_logic.delete_competency(competency_name)

    assert success is False
    assert "is used" in message


def test_save_competencies(competency_logic):
    """Test saving changes to competencies."""
    # Mocking competency_widgets
    competency_widgets = []
    for i in range(competency_logic.ad.md.len('Competency')):
        widget_mock = {
            'competency_name': MagicMock(),
            'display_order': MagicMock(),
            'scope': MagicMock(),
            'expiry': MagicMock(),
            'prerequisite': MagicMock(),
            'nightshift': MagicMock(),
            'bank': MagicMock()
        }
        widget_mock['competency_name'].get.return_value = competency_logic.ad.md.get('Competency', 'Competency Name', i)
        widget_mock['display_order'].get.return_value = str(competency_logic.ad.md.get('Competency', 'Display Order', i))
        widget_mock['scope'].get.return_value = competency_logic.ad.md.get('Competency', 'Scope', i)
        widget_mock['expiry'].get.return_value = str(competency_logic.ad.md.get('Competency', 'Expiry', i))
        widget_mock['prerequisite'].get.return_value = competency_logic.ad.md.get('Competency', 'Prerequisite', i)
        widget_mock['nightshift'].get.return_value = competency_logic.ad.md.get('Competency', 'Nightshift', i)
        widget_mock['bank'].get.return_value = competency_logic.ad.md.get('Competency', 'Bank', i)
        competency_widgets.append(widget_mock)

    # Change a value
    competency_widgets[0]['competency_name'].get.return_value = "New Name"

    num_changes, message = competency_logic.save_competencies(competency_widgets)

    assert num_changes == 1
    assert message == "1 changes saved"
    assert competency_logic.ad.md.get('Competency', 'Competency Name', 0) == "New Name"
