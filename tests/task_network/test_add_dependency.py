import networkx as nx
import pytest

from graft.task_network import (
    Dependee2TasksError,
    DependencyExistsError,
    DependencyIntroducesCycleError,
    Dependent2TaskError,
    InverseDependencyExistsError,
    SelfDependencyError,
    TaskDoesNotExistError,
)


def test_add_dependency_simple(task_network):
    # Given two tasks are present in the network
    task_network.add_task("1")
    task_network.add_task("2")
    assert "1" in task_network._task_attributes_map
    assert "2" in task_network._task_attributes_map

    # When a dependency is created between the tasks
    task_network.add_dependency(uid1="1", uid2="2")

    # Then the dependency is added to task dependencies graph
    assert task_network._task_dependencies.has_edge("1", "2")


def test_add_dependency_dependee_task_absent(task_network):
    # Given a task is present in the network
    task_network.add_task("2")
    assert "2" in task_network._task_attributes_map

    # When a dependency is created where the dependee task is not present in the network
    # Then the appropriate exception is raised
    with pytest.raises(TaskDoesNotExistError) as exc_info:
        task_network.add_dependency(uid1="1", uid2="2")
    assert exc_info.value.uid == "1"


def test_add_dependency_dependent_task_absent(task_network):
    # Given a task is present in the network
    task_network.add_task("1")
    assert "1" in task_network._task_attributes_map

    # When a dependency is created where the dependent task is not present in the network
    # Then the appropriate exception is raised
    with pytest.raises(TaskDoesNotExistError) as exc_info:
        task_network.add_dependency("1", "2")
    assert exc_info.value.uid == "2"


def test_add_dependency_self(task_network):
    # Given a task is present in the network
    task_network.add_task("1")
    assert "1" in task_network._task_attributes_map

    # When a dependency is added between a task and itself
    # Then the appropriate exception is raised
    with pytest.raises(SelfDependencyError) as exc_info:
        task_network.add_dependency("1", "1")
    assert exc_info.value.uid == "1"


def test_add_dependency_already_present(task_network):
    # Given that a dependency exists between two tasks
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_dependency("1", "2")
    assert task_network._task_dependencies.has_edge("1", "2")

    # When a dependency is added that already exists
    # Then the appropriate exception is raised
    with pytest.raises(DependencyExistsError) as exc_info:
        task_network.add_dependency(uid1="1", uid2="2")
    exc_info.value.uid1 == "1"
    exc_info.value.uid2 == "2"


def test_add_dependency_inverse_already_present(task_network):
    # Given that a dependency exists between two tasks
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_dependency("1", "2")
    assert task_network._task_dependencies.has_edge("1", "2")

    # When a dependency is added that is the inverse of an existing dependency
    # Then the appropriate exception is raised
    with pytest.raises(InverseDependencyExistsError) as exc_info:
        task_network.add_dependency(uid1="2", uid2="1")
    exc_info.value.uid1 == "1"
    exc_info.value.uid2 == "2"


def test_dependent_task_already_dependent2_single(task_network):
    # Given the following task dependencies 1 -> 2 -> 3
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_dependency("1", "2")
    task_network.add_dependency("2", "3")
    assert nx.has_path(G=task_network._task_dependencies, source="1", target="3")

    # When a dependency is added between a task and another task that is already a dependent2
    # Then the appropriate exception is raised
    with pytest.raises(Dependent2TaskError) as exc_info:
        task_network.add_dependency(uid1="1", uid2="3")
    expected_digraph = nx.DiGraph((("1", "2"), ("2", "3")))
    assert exc_info.value.uid1 == "1"
    assert exc_info.value.uid2 == "3"
    assert nx.is_isomorphic(G1=exc_info.value.digraph, G2=expected_digraph)


def test_dependent_task_already_dependent2_multiple(task_network):
    # Given the following task dependencies 1 -> (2, 3) -> 4
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_task("4")
    task_network.add_dependency("1", "2")
    task_network.add_dependency("2", "4")
    task_network.add_dependency("1", "3")
    task_network.add_dependency("3", "4")
    assert nx.has_path(G=task_network._task_dependencies, source="1", target="3")

    # When a dependency is added between a task and another task that is already a dependent2
    # Then the appropriate exception is raised
    # Note that both paths from 1 -> 4 are included in the digraph
    with pytest.raises(Dependent2TaskError) as exc_info:
        task_network.add_dependency(uid1="1", uid2="4")
    expected_digraph = nx.DiGraph((("1", "2"), ("2", "4"), ("1", "3"), ("3", "4")))
    exc_info.value.uid1 = "1"
    exc_info.value.uid2 = "4"
    assert nx.is_isomorphic(G1=exc_info.value.digraph, G2=expected_digraph)


def test_dependent_task_already_dependent2_excludes_unrelated_task(task_network):
    # Given the following task dependencies 1 -> 2 -> (3, 4)
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_task("4")
    task_network.add_dependency("1", "2")
    task_network.add_dependency("2", "3")
    task_network.add_dependency("2", "4")
    assert nx.has_path(G=task_network._task_dependencies, source="1", target="3")
    assert nx.has_path(G=task_network._task_dependencies, source="1", target="4")

    # When a dependency is added between a task and another task that is already a dependent2
    # Then the appropriate exception is raised
    # Note that 4 is not included
    with pytest.raises(Dependent2TaskError) as exc_info:
        task_network.add_dependency(uid1="1", uid2="3")
    expected_digraph = nx.DiGraph((("1", "2"), ("2", "3")))
    assert exc_info.value.uid1 == "1"
    assert exc_info.value.uid2 == "3"
    assert nx.is_isomorphic(G1=exc_info.value.digraph, G2=expected_digraph)


def test_dependee2_task_of_dependee_already_dependee_of_dependent(task_network):
    # Given the following task dependencies 1 -> (2, 3)
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_dependency("1", "2")
    task_network.add_dependency("1", "3")

    # When a hierarchy is added
    # And the dependent task is already the dependent of a task dependee2 to the dependee task
    # Then the appropriate exception is raised
    with pytest.raises(Dependee2TasksError) as exc_info:
        task_network.add_dependency("2", "3")
    assert exc_info.value.uid1 == "2"
    assert exc_info.value.uid2 == "3"
    assert exc_info.value.superior_tasks == {"1"}


def test_dependency_introduces_cycle(task_network):
    # Given the following task dependencies 1 -> 2 -> 3
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_dependency("1", "2")
    task_network.add_dependency("2", "3")
    assert nx.has_path(G=task_network._task_dependencies, source="1", target="3")

    # When a dependency is added
    # And a cycle is created
    # Then the appropriate exception is raised
    with pytest.raises(DependencyIntroducesCycleError) as exc_info:
        task_network.add_dependency("3", "1")
    expected_digraph = nx.DiGraph((("1", "2"), ("2", "3")))
    assert exc_info.value.uid1 == "3"
    assert exc_info.value.uid2 == "1"
    assert nx.is_isomorphic(G1=exc_info.value.digraph, G2=expected_digraph)
