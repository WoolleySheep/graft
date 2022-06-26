import pytest

from graft.task_network import (
    DependencyDoesNotExistError,
    SelfDependencyError,
    TaskDoesNotExistError,
)


def test_remove_dependency_simple(task_network):
    # Given a task dependency 1 -> 2
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_dependency(uid1="1", uid2="2")
    assert task_network._task_dependencies.has_edge(source="1", target="2")

    # When the dependency is removed
    task_network.remove_dependency(uid1="1", uid2="2")

    # Then the edge is no longer present in the dependencies graph
    # And both tasks are still present in the network
    assert not task_network._task_dependencies.has_edge(source="1", target="2")
    assert "1" in task_network._task_attributes_map
    assert "2" in task_network._task_attributes_map


def test_remove_dependency_no_dependee_task(task_network):
    # Given a task is present in the network
    task_network.add_task("2")
    assert "2" in task_network._task_attributes_map

    # When a dependency is removed where the dependee task is not present in the network
    # Then the appropriate exception is raised
    with pytest.raises(TaskDoesNotExistError) as exc_info:
        task_network.remove_dependency("1", "2")
    assert exc_info.value.uid == "1"


def test_remove_dependency_no_dependent_task(task_network):
    # Given a task is present in the network
    task_network.add_task("1")
    assert "1" in task_network._task_attributes_map

    # When a dependency is removed where the dependent task is not present in the network
    # Then the appropriate exception is raised
    with pytest.raises(TaskDoesNotExistError) as exc_info:
        task_network.remove_dependency("1", "2")
    assert exc_info.value.uid == "2"


def test_remove_dependency_self(task_network):
    # Given a task is present in the network
    task_network.add_task("1")
    assert "1" in task_network._task_attributes_map

    # When a dependency is removed between a task and itself
    # Then the appropriate exception is raised
    with pytest.raises(SelfDependencyError) as exc_info:
        task_network.remove_dependency("1", "1")
    assert exc_info.value.uid == "1"


def test_remove_dependency_no_dependency(task_network):
    # Given that two tasks exist in a network
    # And there is no dependency between them
    task_network.add_task("1")
    task_network.add_task("2")
    assert not task_network._task_dependencies.has_edge("1", "2")

    # When a dependency is removed that does not exist
    # Then the appropriate exception is raised
    with pytest.raises(DependencyDoesNotExistError) as exc_info:
        task_network.remove_dependency(uid1="1", uid2="2")
    exc_info.value.uid1 == "1"
    exc_info.value.uid2 == "2"
