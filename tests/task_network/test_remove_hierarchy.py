import pytest

from graft.task_network import (
    HierarchyDoesNotExistError,
    SelfHierarchyError,
    TaskDoesNotExistError,
)


def test_remove_hierarchy_simple(task_network):
    # Given a task hierarchy 1 -> 2
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_hierarchy(uid1="1", uid2="2")
    assert task_network._task_hierarchy.has_edge(source="1", target="2")

    # When the hierarchy is removed
    task_network.remove_hierarchy(uid1="1", uid2="2")

    # Then the edge is no longer present in the hierarchy graph
    # And both tasks are still present in the network
    assert not task_network._task_hierarchy.has_edge(source="1", target="2")
    assert "1" in task_network._task_attributes_map
    assert "2" in task_network._task_attributes_map


def test_remove_hierarchy_no_supertask(task_network):
    # Given a task is present in the network
    task_network.add_task("2")
    assert "2" in task_network._task_attributes_map

    # When a hierarchy is removed where the supertask is not present in the network
    # Then the appropriate exception is raised
    with pytest.raises(TaskDoesNotExistError) as exc_info:
        task_network.remove_hierarchy("1", "2")
    assert exc_info.value.uid == "1"


def test_remove_hierarchy_no_subtask(task_network):
    # Given a task is present in the network
    task_network.add_task("1")
    assert "1" in task_network._task_attributes_map

    # When a hierarchy is removed where the subtask is not present in the network
    # Then the appropriate exception is raised
    with pytest.raises(TaskDoesNotExistError) as exc_info:
        task_network.remove_hierarchy("1", "2")
    assert exc_info.value.uid == "2"


def test_remove_hierarchy_self(task_network):
    # Given a task is present in the network
    task_network.add_task("1")
    assert "1" in task_network._task_attributes_map

    # When a hierarchy is removed between a task and itself
    # Then the appropriate exception is raised
    with pytest.raises(SelfHierarchyError) as exc_info:
        task_network.remove_hierarchy("1", "1")
    assert exc_info.value.uid == "1"


def test_remove_hierarchy_no_hierarchy(task_network):
    # Given that two tasks exist in a network
    # And there is no hierarchy between them
    task_network.add_task("1")
    task_network.add_task("2")
    assert not task_network._task_hierarchy.has_edge("1", "2")

    # When a hierarchy is removed that does not exist
    # Then the appropriate exception is raised
    with pytest.raises(HierarchyDoesNotExistError) as exc_info:
        task_network.remove_hierarchy(uid1="1", uid2="2")
    exc_info.value.uid1 == "1"
    exc_info.value.uid2 == "2"
