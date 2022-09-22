import pytest

from graft.acyclic_digraph import AcyclicDiGraph
from graft.constrained_graph import ConstrainedGraph
from graft.task_network import TaskNetwork


@pytest.fixture
def task_network() -> TaskNetwork:
    """Return an empty task network."""
    return TaskNetwork(
        task_attributes_map={},
        task_hierarchy=ConstrainedGraph(),
        task_dependencies=AcyclicDiGraph(),
    )
