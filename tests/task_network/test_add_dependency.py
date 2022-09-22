import networkx as nx
import pytest
from graft.task_network import (
    DependencyCycleInferiorOf1DownstreamOf2,
    DependencyCycleInferiorOf2UpstreamOf1,
    DependencyDownstreamCycleError,
    DependencyExistsError,
    DependencyHierarchyClashError,
    DependencyHierarchyExtendedClashError,
    DependencyIntroducesCycleError,
    InverseDependencyExistsError,
    SelfDependencyError,
    TaskDoesNotExistError,
    TaskNetwork,
    UnnecessaryDependencyError,
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


def test_hierarchy_relationship_1_supertask_2(task_network: TaskNetwork):
    # Given the following task hierarchy 1 -> 2
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_hierarchy("1", "2")

    # When a dependency is added
    # And there is already a hierarchical relationship between the two tasks
    # Then the appropriate exception is raised
    with pytest.raises(DependencyHierarchyClashError) as exc_info:
        task_network.add_dependency("1", "2")
    assert exc_info.value.supertask == "1"
    assert exc_info.value.subtask == "2"
    assert exc_info.value.uid1 == "1"
    assert exc_info.value.uid2 == "2"


def test_hierarchy_relationship_2_supertask_1(task_network: TaskNetwork):
    # Given the following task hierarchy 1 -> 2
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_hierarchy("1", "2")

    # When a dependency is added
    # And there is already a hierarchical relationship between the two tasks
    # Then the appropriate exception is raised
    with pytest.raises(DependencyHierarchyClashError) as exc_info:
        task_network.add_dependency("2", "1")
    assert exc_info.value.supertask == "1"
    assert exc_info.value.subtask == "2"
    assert exc_info.value.uid1 == "2"
    assert exc_info.value.uid2 == "1"


def test_1_superior_2(task_network: TaskNetwork):
    # Given the following task hierarchy 1 -> 2 -> 3
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    assert nx.has_path(G=task_network._task_hierarchy, source="1", target="3")

    # When a dependency is added
    # And task 1 is superior to task 2
    # Then the appropriate exception is raised
    with pytest.raises(DependencyHierarchyExtendedClashError) as exc_info:
        task_network.add_dependency("1", "3")
    assert exc_info.value.uid1 == "1"
    assert exc_info.value.uid2 == "3"
    # TODO: Add digraph of heirarchy structure to exception


def test_2_superior_1(task_network: TaskNetwork):
    # Given the following task hierarchy 1 -> 2 -> 3
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    assert nx.has_path(G=task_network._task_hierarchy, source="1", target="3")

    # When a dependency is added
    # And task 1 is superior to task 2
    # Then the appropriate exception is raised
    with pytest.raises(DependencyHierarchyExtendedClashError) as exc_info:
        task_network.add_dependency("3", "1")
    assert exc_info.value.uid1 == "3"
    assert exc_info.value.uid2 == "1"
    # TODO: Add digraph of heirarchy structure to exception


def test_1_downstream_2(task_network: TaskNetwork):
    # Given the following task network
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_dependency("1", "2")
    task_network.add_hierarchy("2", "3")

    # When a dependency is added
    # And task 2 is downstream of task 1
    # Then the appropriate exception is raised
    with pytest.raises(DependencyDownstreamCycleError) as exc_info:
        task_network.add_dependency("3", "1")
    assert exc_info.value.uid1 == "3"
    assert exc_info.value.uid2 == "1"
    # TODO: Add a more complex test case for this


def test_inferior_2_upstream_1(task_network: TaskNetwork):
    # Given the following task network
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_task("4")
    task_network.add_dependency("2", "3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("3", "4")

    # When a dependency is added
    # And an inferior of task 2 is upstream of task 1
    # Then the appropriate exception is raised
    with pytest.raises(DependencyCycleInferiorOf2UpstreamOf1) as exc_info:
        task_network.add_dependency("4", "1")
    assert exc_info.value.uid1 == "4"
    assert exc_info.value.uid2 == "1"


def test_inferior_1_downstream_2(task_network: TaskNetwork):
    # Given the following task network
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_dependency("1", "2")
    task_network.add_hierarchy("3", "2")

    with pytest.raises(DependencyCycleInferiorOf1DownstreamOf2) as exc_info:
        task_network.add_dependency("3", "1")
    assert exc_info.value.uid1 == "3"
    assert exc_info.value.uid2 == "1"


def test_unnecessary_dependency_1(task_network: TaskNetwork):
    # Given the following task network
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_dependency("2", "3")

    # When a dependency is added that overwrites an existing dependency
    # Then an appropriate exception is raised
    with pytest.raises(UnnecessaryDependencyError) as exc_info:
        task_network.add_dependency("1", "3")
    assert exc_info.value.uid1 == "1"
    assert exc_info.value.uid2 == "3"


def test_unnecessary_dependency_2(task_network: TaskNetwork):
    # Given the following task network
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_dependency("1", "3")

    # When a dependency is added that is already captured by an an existing dependency
    # Then an appropriate exception is raised
    with pytest.raises(UnnecessaryDependencyError) as exc_info:
        task_network.add_dependency("2", "3")
    assert exc_info.value.uid1 == "2"
    assert exc_info.value.uid2 == "3"


def test_unnecessary_dependency_3(task_network: TaskNetwork):
    # Given the following task network
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("2", "3")
    task_network.add_dependency("1", "3")

    # When a dependency is added that that overwrites an existing dependency
    # Then an appropriate exception is raised
    with pytest.raises(UnnecessaryDependencyError) as exc_info:
        task_network.add_dependency("1", "2")
    assert exc_info.value.uid1 == "1"
    assert exc_info.value.uid2 == "2"


def test_unnecessary_dependency_4(task_network: TaskNetwork):
    # Given the following task network
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_task("4")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    task_network.add_dependency("1", "4")

    # When a dependency is added that is already captured by an an existing dependency
    # Then an appropriate exception is raised
    with pytest.raises(UnnecessaryDependencyError) as exc_info:
        task_network.add_dependency("3", "4")
    assert exc_info.value.uid1 == "3"
    assert exc_info.value.uid2 == "4"


def test_unnecessary_dependency_5(task_network: TaskNetwork):
    # Given the following task network
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_task("4")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("3", "4")
    task_network.add_dependency("1", "3")

    # When a dependency is added that is already captured by an an existing dependency
    # Then an appropriate exception is raised
    with pytest.raises(UnnecessaryDependencyError) as exc_info:
        task_network.add_dependency("2", "4")
    assert exc_info.value.uid1 == "2"
    assert exc_info.value.uid2 == "4"


def test_unnecessary_dependency_6(task_network: TaskNetwork):
    # Given the following task network
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_task("4")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("3", "4")
    task_network.add_dependency("1", "4")

    # When a dependency is added that that overwrites an existing dependency
    # Then an appropriate exception is raised
    with pytest.raises(UnnecessaryDependencyError) as exc_info:
        task_network.add_dependency("2", "3")
    assert exc_info.value.uid1 == "2"
    assert exc_info.value.uid2 == "3"
