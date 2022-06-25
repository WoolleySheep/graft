from re import U

import pytest

from graft.constrained_graph import ConstrainedGraph
from graft.task_network import (
    HasDependeeTasksError,
    HasDependentTasksError,
    HasSubTasksError,
    HasSuperTasksError,
    HierarchyExistsError,
    TaskDoesNotExistError,
    TaskNetwork,
)


@pytest.fixture
def task_network() -> TaskNetwork:
    return TaskNetwork(
        task_attributes_map={},
        task_hierarchy=ConstrainedGraph(),
        task_dependencies=ConstrainedGraph(),
    )


def test_add_task(task_network):
    assert "1" not in task_network._task_attributes_map
    assert "1" not in task_network._task_hierarchy
    assert "1" not in task_network._task_dependencies

    # When the task is added to the network
    task_network.add_task("1")

    # Then it is added to each of the components
    assert "1" in task_network._task_attributes_map
    assert "1" in task_network._task_hierarchy
    assert "1" in task_network._task_dependencies


def test_remove_task_when_exists_and_no_relationships(task_network):
    # Given a task  exists in a network
    # And has no relationship to any other tasks
    task_network.add_task("1")
    assert "1" in task_network._task_attributes_map
    assert "1" in task_network._task_hierarchy
    assert "1" in task_network._task_dependencies

    # When the task is removed from the network
    task_network.remove_task("1")

    # Then it is removed from each of the components
    assert "1" not in task_network._task_attributes_map
    assert "1" not in task_network._task_hierarchy
    assert "1" not in task_network._task_dependencies


def test_remove_task_when_does_not_exist(task_network):
    # Given a task is not present in the network
    assert "1" not in task_network._task_attributes_map
    assert "1" not in task_network._task_hierarchy
    assert "1" not in task_network._task_dependencies

    # When the task is removed from the network
    # Then the appropriate is raised
    with pytest.raises(TaskDoesNotExistError) as exc_info:
        task_network.remove_task("1")
    assert exc_info.value.uid == "1"


def test_remove_task_when_has_supertask(task_network):
    # Given that a task is present in the network
    # And has a supertask
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_hierarchy("1", "2")
    assert task_network._task_hierarchy.has_edge("1", "2")

    # When the task is removed from the network
    # Then the appropriate is raised
    with pytest.raises(HasSuperTasksError) as exc_info:
        task_network.remove_task("2")
    assert exc_info.value.uid == "2"
    assert exc_info.value.supertasks == {"1"}


def test_remove_task_when_has_subtask(task_network):
    # Given that a task is present in the network
    # And has a subtask
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_hierarchy("1", "2")
    assert task_network._task_hierarchy.has_edge("1", "2")

    # When the task is removed from the network
    # Then the appropriate exception is raised
    with pytest.raises(HasSubTasksError) as exc_info:
        task_network.remove_task("1")
    assert exc_info.value.uid == "1"
    assert exc_info.value.subtasks == {"2"}


def test_remove_task_when_has_dependee_task(task_network):
    # Given that a task is present in the network
    # And has a dependent task
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_dependency("1", "2")
    assert task_network._task_dependencies.has_edge("1", "2")

    # When the task is removed from the network
    # Then the appropriate is raised
    with pytest.raises(HasDependeeTasksError) as exc_info:
        task_network.remove_task("2")
    assert exc_info.value.uid == "2"
    assert exc_info.value.dependee_tasks == {"1"}


def test_remove_task_when_has_dependent_task(task_network):
    # Given that a task is present in the network
    # And has a dependent task
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_dependency("1", "2")
    assert task_network._task_dependencies.has_edge("1", "2")

    # When the task is removed from the network
    # Then the appropriate is raised
    with pytest.raises(HasDependentTasksError) as exc_info:
        task_network.remove_task("1")
    assert exc_info.value.uid == "1"
    assert exc_info.value.dependent_tasks == {"2"}


def test_add_hierarchy_simple(task_network):
    # Given two tasks are present in the network
    task_network.add_task("1")
    task_network.add_task("2")
    assert "1" in task_network._task_attributes_map
    assert "2" in task_network._task_attributes_map

    # When a hierarchy is created between the tasks
    task_network.add_hierarchy("1", "2")

    # Then the hierarchy is added to task hierarchy graph
    assert task_network._task_hierarchy.has_edge("1", "2")


def test_add_hierarchy_superior_task_absent(task_network):
    # Given a task is present in the network
    task_network.add_task("2")
    assert "2" in task_network._task_attributes_map

    # When a hierarchy is created where the superior task is not present in the network
    # Then the appropriate exception is raised
    with pytest.raises(TaskDoesNotExistError) as exc_info:
        task_network.add_hierarchy("1", "2")
    assert exc_info.value.uid == "1"


def test_add_hierarchy_inferior_task_absent(task_network):
    # Given a task is present in the network
    task_network.add_task("1")
    assert "1" in task_network._task_attributes_map

    # When a hierarchy is created where the inferior task is not present in the network
    # Then the appropriate exception is raised
    with pytest.raises(TaskDoesNotExistError) as exc_info:
        task_network.add_hierarchy("1", "2")
    assert exc_info.value.uid == "2"


def test_add_hierarchy_already_present(task_network):
    # Given that a hierarchy exists between two tasks
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_hierarchy("1", "2")
    assert task_network._task_hierarchy.has_edge("1", "2")

    # When a hierarchy is added that already exists
    # Then the appropriate exception is raised
    with pytest.raises(HierarchyExistsError) as exc_info:
        task_network.add_hierarchy(uid1="1", uid2="2")
    exc_info.value.uid1 == "1"
    exc_info.value.uid2 == "2"
