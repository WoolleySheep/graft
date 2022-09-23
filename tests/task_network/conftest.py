import datetime

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


@pytest.fixture
def datetime_example() -> datetime.datetime:
    """Return a datetime instance."""
    return datetime.datetime(2020, 1, 1)


@pytest.fixture
def datetime_earlier_example(datetime_example: datetime.datetime) -> datetime.datetime:
    """Return a datetime instance earlier than datetime_example."""
    return datetime_example - datetime.timedelta(days=1)


@pytest.fixture
def datetime_later_example(datetime_example: datetime.datetime) -> datetime.datetime:
    """Return a datetime instance later than datetime_example."""
    return datetime_example + datetime.timedelta(days=1)
