import networkx as nx
import pytest
from numpy import source

from graft.constrained_graph import ConstrainedGraph
from graft.task_network import (
    HasDependeeTasksError,
    HasDependentTasksError,
    HasSubTasksError,
    HasSuperTasksError,
    HierarchyDoesNotExistError,
    HierarchyExistsError,
    HierarchyIntroducesCycleError,
    InferiorTaskError,
    InverseHierarchyExistsError,
    SelfHierarchyError,
    SuperiorTasksError,
    TaskDoesNotExistError,
    TaskNetwork,
)


@pytest.fixture
def task_network() -> TaskNetwork:
    # Return an empty task network
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


def test_inferior_task_already_inferior_single(task_network):
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


def test_inferior_task_already_inferior_multiple(task_network):
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


def test_inferior_task_already_inferior_unrelated_task(task_network):
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


def test_superior_task_of_superior_already_supertask_of_inferior(task_network):
    # Given the following task hierarchy 1 -> (2, 3)
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("1", "3")

    # When a hierarchy is added
    # And the inferior task is already the subtask of a task superior to the superior task
    # Then the appropriate exception is raised
    with pytest.raises(SuperiorTasksError) as exc_info:
        task_network.add_hierarchy("2", "3")
    assert exc_info.value.uid1 == "2"
    assert exc_info.value.uid2 == "3"
    assert exc_info.value.superior_tasks == {"1"}


def test_introduces_cycle(task_network):
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


def test_remove_hierarchy_no_superior_task(task_network):
    # Given a task is present in the network
    task_network.add_task("2")
    assert "2" in task_network._task_attributes_map

    # When a hierarchy is removed where the superior task is not present in the network
    # Then the appropriate exception is raised
    with pytest.raises(TaskDoesNotExistError) as exc_info:
        task_network.remove_hierarchy("1", "2")
    assert exc_info.value.uid == "1"


def test_remove_hierarchy_no_inferior_task(task_network):
    # Given a task is present in the network
    task_network.add_task("1")
    assert "1" in task_network._task_attributes_map

    # When a hierarchy is removed where the inferior task is not present in the network
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
