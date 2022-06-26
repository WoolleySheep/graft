import networkx as nx
import pytest

from graft.task_network import (
    HierarchyExistsError,
    HierarchyIntroducesCycleError,
    InferiorTaskError,
    InverseHierarchyExistsError,
    SelfHierarchyError,
    SuperiorTasksError,
    TaskCycleError,
    TaskDoesNotExistError,
)


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


def test_add_hierarchy_self(task_network):
    # Given a task is present in the network
    task_network.add_task("1")
    assert "1" in task_network._task_attributes_map

    # When a hierarchy is added between a task and itself
    # Then the appropriate exception is raised
    with pytest.raises(SelfHierarchyError) as exc_info:
        task_network.add_hierarchy("1", "1")
    assert exc_info.value.uid == "1"


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


def test_add_hierarchy_inverse_already_present(task_network):
    # Given that a hierarchy exists between two tasks
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_hierarchy("1", "2")
    assert task_network._task_hierarchy.has_edge("1", "2")

    # When a hierarchy is added that is the inverse of an existing hierarchy
    # Then the appropriate exception is raised
    with pytest.raises(InverseHierarchyExistsError) as exc_info:
        task_network.add_hierarchy(uid1="2", uid2="1")
    exc_info.value.uid1 == "1"
    exc_info.value.uid2 == "2"


def test_subtask_task_already_inferior_single(task_network):
    # Given the following task hierarchy 1 -> 2 -> 3
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    assert nx.has_path(G=task_network._task_hierarchy, source="1", target="3")

    # When a hierarchy is added between a task and another task that is already its inferior
    # Then the appropriate exception is raised
    with pytest.raises(InferiorTaskError) as exc_info:
        task_network.add_hierarchy(uid1="1", uid2="3")
    expected_digraph = nx.DiGraph((("1", "2"), ("2", "3")))
    assert exc_info.value.uid1 == "1"
    assert exc_info.value.uid2 == "3"
    assert nx.is_isomorphic(G1=exc_info.value.digraph, G2=expected_digraph)


def test_subtask_task_already_inferior_multiple(task_network):
    # Given the following task hierarchy 1 -> (2, 3) -> 4
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_task("4")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "4")
    task_network.add_hierarchy("1", "3")
    task_network.add_hierarchy("3", "4")
    assert nx.has_path(G=task_network._task_hierarchy, source="1", target="3")

    # When a hierarchy is added between a task and another task that is already its inferior
    # Then the appropriate exception is raised
    # Note that boths paths from 1 -> 4 are included in the digraph
    with pytest.raises(InferiorTaskError) as exc_info:
        task_network.add_hierarchy(uid1="1", uid2="4")
    expected_digraph = nx.DiGraph((("1", "2"), ("2", "4"), ("1", "3"), ("3", "4")))
    exc_info.value.uid1 = "1"
    exc_info.value.uid2 = "4"
    assert nx.is_isomorphic(G1=exc_info.value.digraph, G2=expected_digraph)


def test_subtask_task_already_inferior_unrelated_task(task_network):
    # Given the following task hierarchy 1 -> 2 -> (3, 4)
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_task("4")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    task_network.add_hierarchy("2", "4")
    assert nx.has_path(G=task_network._task_hierarchy, source="1", target="3")
    assert nx.has_path(G=task_network._task_hierarchy, source="1", target="4")

    # When a hierarchy is added between a task and another task that is already its inferior
    # Then the appropriate exception is raised
    # Note that 4 is not included
    with pytest.raises(InferiorTaskError) as exc_info:
        task_network.add_hierarchy(uid1="1", uid2="3")
    expected_digraph = nx.DiGraph((("1", "2"), ("2", "3")))
    assert exc_info.value.uid1 == "1"
    assert exc_info.value.uid2 == "3"
    assert nx.is_isomorphic(G1=exc_info.value.digraph, G2=expected_digraph)


def test_superior_task_of_supertask_already_supertask_of_subtask(task_network):
    # Given the following task hierarchy 1 -> (2, 3)
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("1", "3")

    # When a hierarchy is added
    # And the subtask task is already the subtask of a task superior to the supertask
    # Then the appropriate exception is raised
    with pytest.raises(SuperiorTasksError) as exc_info:
        task_network.add_hierarchy("2", "3")
    assert exc_info.value.uid1 == "2"
    assert exc_info.value.uid2 == "3"
    assert exc_info.value.superior_tasks == {"1"}


def test_hierarchy_introduces_cycle(task_network):
    # Given the following task hierarchy 1 -> 2 -> 3
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    assert nx.has_path(G=task_network._task_hierarchy, source="1", target="3")

    # When a hierarchy is added
    # And a cycle is created
    # Then the appropriate exception is raised
    with pytest.raises(HierarchyIntroducesCycleError) as exc_info:
        task_network.add_hierarchy("3", "1")
    expected_digraph = nx.DiGraph((("1", "2"), ("2", "3")))
    assert exc_info.value.uid1 == "3"
    assert exc_info.value.uid2 == "1"
    assert nx.is_isomorphic(G1=exc_info.value.digraph, G2=expected_digraph)


def test_superior_of_1_upstream_of_2(task_network):
    # Given the following task hierarchy
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_task("4")
    task_network.add_dependency("1", "2")
    task_network.add_hierarchy("1", "3")
    task_network.add_hierarchy("2", "4")

    # When a hierarchy is added
    # And a superior of the supertask is upstream of the subtask
    # Then the appropriate exception is raised
    with pytest.raises(TaskCycleError) as exc_info:
        task_network.add_hierarchy("3", "4")
    assert exc_info.value.uid1 == "3"
    assert exc_info.value.uid2 == "4"
    assert exc_info.value.problem_tasks == {"1"}


def test_1_upstream_of_2(task_network):
    # Given the following task hierarchy
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_dependency("1", "2")
    task_network.add_hierarchy("2", "3")

    # When a hierarchy is added
    # And the supertask is upstream of the subtask
    # Then the appropriate exception is raised
    with pytest.raises(TaskCycleError) as exc_info:
        task_network.add_hierarchy("1", "3")
    assert exc_info.value.uid1 == "1"
    assert exc_info.value.uid2 == "3"
    assert exc_info.value.problem_tasks == {"1"}
