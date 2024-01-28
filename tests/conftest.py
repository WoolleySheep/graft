import pytest

from graft import domain
from graft.domain import tasks


@pytest.fixture()
def empty_system() -> domain.System:
    """Create an empty system."""
    return domain.System(
        task_system=tasks.System(
            attributes_register=tasks.AttributesRegister(),
            hierarchy_graph=tasks.HierarchyGraph(),
            dependency_graph=tasks.DependencyGraph(),
        )
    )
