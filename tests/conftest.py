"""Pytest configuration and fixtures."""

import pytest

from graft import domain
from graft.domain import tasks


@pytest.fixture()
def empty_system() -> domain.System:
    """Return an empty system."""
    return domain.System(task_system=tasks.System.empty())
