"""Unit tests for `System.create_dependency`."""

import copy
from unittest import mock

import pytest

from graft import domain
from graft.domain import tasks
from graft.domain.tasks.network_graph import NetworkGraph
from graft.layers import logic


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_success(data_layer_mock: mock.MagicMock) -> None:
    """Test the create_dependency method succeeds as expected."""
    system = domain.System.empty()

    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)

    system.add_task(dependee_task)
    system.add_task(dependent_task)

    system_with_dependency = copy.deepcopy(system)
    system_with_dependency.add_task_dependency(
        dependee_task=dependee_task, dependent_task=dependent_task
    )

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.create_task_dependency(
        dependee_task=dependee_task, dependent_task=dependent_task
    )

    data_layer_mock.load_system.assert_called_once()
    data_layer_mock.save_system.assert_called_once_with(system_with_dependency)


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependee_task_not_exist(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when the dependee task does not exist."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)
    absent_dependee_task = tasks.UID(2)

    system = domain.System.empty()
    system.add_task(dependee_task)
    system.add_task(dependent_task)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.TaskDoesNotExistError) as exc_info:
        logic_layer.create_task_dependency(
            dependee_task=absent_dependee_task, dependent_task=dependent_task
        )
    assert exc_info.value.task == absent_dependee_task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependent_task_not_exist(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when the dependent task does not exist."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)
    absent_dependent_task = tasks.UID(2)

    system = domain.System.empty()
    system.add_task(dependee_task)
    system.add_task(dependent_task)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.TaskDoesNotExistError) as exc_info:
        logic_layer.create_task_dependency(
            dependee_task=dependee_task, dependent_task=absent_dependent_task
        )
    assert exc_info.value.task == absent_dependent_task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependent_task_dependee_task_the_same(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when the dependent task and the dependee task are the same."""
    task = tasks.UID(0)

    system = domain.System.empty()
    system.add_task(task)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyLoopError) as exc_info:
        logic_layer.create_task_dependency(dependee_task=task, dependent_task=task)
    assert exc_info.value.task == task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependency_already_exists(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when the dependency already exists."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)

    system = domain.System.empty()
    system.add_task(dependee_task)
    system.add_task(dependent_task)
    system.add_task_dependency(
        dependee_task=dependee_task, dependent_task=dependent_task
    )

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyAlreadyExistsError) as exc_info:
        logic_layer.create_task_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )
    assert exc_info.value.dependee_task == dependee_task
    assert exc_info.value.dependent_task == dependent_task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_inverse_hierarchy_already_exists(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when the inverse hierarchy already exists."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)

    system = domain.System.empty()
    system.add_task(dependee_task)
    system.add_task(dependent_task)
    system.add_task_dependency(
        dependee_task=dependee_task, dependent_task=dependent_task
    )

    expected_subgraph = tasks.DependencyGraph()
    expected_subgraph.add_task(dependee_task)
    expected_subgraph.add_task(dependent_task)
    expected_subgraph.add_dependency(dependee_task, dependent_task)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyIntroducesCycleError) as exc_info:
        logic_layer.create_task_dependency(
            dependee_task=dependent_task, dependent_task=dependee_task
        )
    assert exc_info.value.dependee_task == dependent_task
    assert exc_info.value.dependent_task == dependee_task
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_introduces_cycle(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when the dependency introduces a cycle."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task_dependency(dependee_task=task0, dependent_task=task1)
    system.add_task_dependency(dependee_task=task1, dependent_task=task2)

    expected_subgraph = tasks.DependencyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_dependency(dependee_task=task0, dependent_task=task1)
    expected_subgraph.add_dependency(dependee_task=task1, dependent_task=task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyIntroducesCycleError) as exc_info:
        logic_layer.create_task_dependency(dependee_task=task2, dependent_task=task0)
    assert exc_info.value.dependee_task == task2
    assert exc_info.value.dependent_task == task0
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_introduces_cycle_prunes_subgraph_correctly(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when the dependency introduces a cycle and prunes the subgraph correctly."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task_dependency(dependee_task=task0, dependent_task=task1)
    system.add_task_dependency(dependee_task=task1, dependent_task=task2)
    system.add_task_dependency(dependee_task=task1, dependent_task=task3)

    expected_subgraph = tasks.DependencyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_dependency(task0, task1)
    expected_subgraph.add_dependency(task1, task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyIntroducesCycleError) as exc_info:
        logic_layer.create_task_dependency(dependee_task=task2, dependent_task=task0)
    assert exc_info.value.dependee_task == task2
    assert exc_info.value.dependent_task == task0
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_success_multiple_paths_allowed(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method succeeds even when there are multiple paths.

    This is different from the hierarchy graph, which does not allow multiple
    paths. This test is just here as a safety check in case something changes
    unexpectedly.
    """
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task_dependency(dependee_task=task0, dependent_task=task1)
    system.add_task_dependency(dependee_task=task1, dependent_task=task2)

    system_with_multiple_paths = copy.deepcopy(system)
    system_with_multiple_paths.add_task_dependency(
        dependee_task=task0, dependent_task=task2
    )

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.create_task_dependency(dependee_task=task0, dependent_task=task2)

    data_layer_mock.load_system.assert_called_once()
    data_layer_mock.save_system.assert_called_once_with(system_with_multiple_paths)


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_hierarchy_from_dependee_task_to_dependent_task(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when a hierarchy already exists from the dependee-task to the dependent-task."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)

    system = domain.System.empty()
    system.add_task(dependee_task)
    system.add_task(dependent_task)
    system.add_task_hierarchy(supertask=dependee_task, subtask=dependent_task)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(dependee_task)
    expected_subgraph.add_task(dependent_task)
    expected_subgraph.add_hierarchy(dependee_task, dependent_task)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyBetweenHierarchyLevelsError) as exc_info:
        logic_layer.create_task_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )
    assert exc_info.value.dependee_task == dependee_task
    assert exc_info.value.dependent_task == dependent_task
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_hierarchy_path_from_dependee_task_to_dependent_task(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when a hierarchy path already exists from the dependee-task to the dependent-task."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task_hierarchy(supertask=task0, subtask=task1)
    system.add_task_hierarchy(supertask=task1, subtask=task2)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task1, task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyBetweenHierarchyLevelsError) as exc_info:
        logic_layer.create_task_dependency(dependee_task=task0, dependent_task=task2)
    assert exc_info.value.dependee_task == task0
    assert exc_info.value.dependent_task == task2
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_hierarchy_from_dependent_task_to_dependee_task(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when a hierarchy already exists from the dependent-task to the dependee-task."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)

    system = domain.System.empty()
    system.add_task(dependee_task)
    system.add_task(dependent_task)
    system.add_task_hierarchy(supertask=dependent_task, subtask=dependee_task)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(dependee_task)
    expected_subgraph.add_task(dependent_task)
    expected_subgraph.add_hierarchy(dependent_task, dependee_task)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyBetweenHierarchyLevelsError) as exc_info:
        logic_layer.create_task_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )
    assert exc_info.value.dependee_task == dependee_task
    assert exc_info.value.dependent_task == dependent_task
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_hierarchy_path_from_dependent_task_to_dependee_task(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when a hierarchy path already exists from the dependee-task to the dependent-task."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task_hierarchy(supertask=task0, subtask=task1)
    system.add_task_hierarchy(supertask=task1, subtask=task2)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task1, task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyBetweenHierarchyLevelsError) as exc_info:
        logic_layer.create_task_dependency(dependee_task=task2, dependent_task=task0)
    assert exc_info.value.dependee_task == task2
    assert exc_info.value.dependent_task == task0
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_introduces_network_cycle(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when a network cycle is introduced."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task_dependency(task0, task1)
    system.add_task_hierarchy(task1, task2)

    expected_subgraph = NetworkGraph.empty()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_dependency(task0, task1)
    expected_subgraph.add_hierarchy(task1, task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyIntroducesNetworkCycleError) as exc_info:
        logic_layer.create_task_dependency(task2, task0)
    assert exc_info.value.dependee_task == task2
    assert exc_info.value.dependent_task == task0
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_path_from_inferior_task_of_dependent_task_to_dependee_task(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when a stream path already exists from an inferior task of the dependent-task to the dependee-task."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)
    task4 = tasks.UID(4)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)
    system.add_task_hierarchy(task0, task1)
    system.add_task_dependency(task1, task2)
    system.add_task_dependency(task2, task3)
    system.add_task_hierarchy(task3, task4)

    expected_subgraph = NetworkGraph.empty()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_task(task3)
    expected_subgraph.add_task(task4)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_dependency(task1, task2)
    expected_subgraph.add_dependency(task2, task3)
    expected_subgraph.add_hierarchy(task3, task4)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyIntroducesNetworkCycleError) as exc_info:
        logic_layer.create_task_dependency(task4, task0)
    assert exc_info.value.dependee_task == task4
    assert exc_info.value.dependent_task == task0
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_path_from_dependent_task_to_inferior_task_of_dependee_task(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when a stream path already exists from the dependent-task to an inferior task of the dependee-task."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)
    task4 = tasks.UID(4)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)
    system.add_task_dependency(task0, task1)
    system.add_task_hierarchy(task1, task2)
    system.add_task_dependency(task2, task3)
    system.add_task_hierarchy(task4, task3)

    expected_subgraph = NetworkGraph.empty()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_task(task3)
    expected_subgraph.add_task(task4)
    expected_subgraph.add_dependency(task0, task1)
    expected_subgraph.add_hierarchy(task1, task2)
    expected_subgraph.add_dependency(task2, task3)
    expected_subgraph.add_hierarchy(task4, task3)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyIntroducesNetworkCycleError) as exc_info:
        logic_layer.create_task_dependency(task4, task0)
    assert exc_info.value.dependee_task == task4
    assert exc_info.value.dependent_task == task0
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_path_from_inferior_task_of_dependent_task_to_inferior_task_of_dependee_task(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when a stream path already exists from an inferior task of the dependent-task to an inferior task of the dependee-task."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)
    task4 = tasks.UID(4)
    task5 = tasks.UID(5)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)
    system.add_task(task5)
    system.add_task_hierarchy(task0, task1)
    system.add_task_dependency(task1, task2)
    system.add_task_hierarchy(task2, task3)
    system.add_task_dependency(task3, task4)
    system.add_task_hierarchy(task5, task4)

    expected_subgraph = NetworkGraph.empty()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_task(task3)
    expected_subgraph.add_task(task4)
    expected_subgraph.add_task(task5)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_dependency(task1, task2)
    expected_subgraph.add_hierarchy(task2, task3)
    expected_subgraph.add_dependency(task3, task4)
    expected_subgraph.add_hierarchy(task5, task4)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyIntroducesNetworkCycleError) as exc_info:
        logic_layer.create_task_dependency(task5, task0)
    assert exc_info.value.dependee_task == task5
    assert exc_info.value.dependent_task == task0
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependency_duplication_with_dependee_task_superior_task(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when their is a dependency duplication with the superior-task of the dependee-task."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task_hierarchy(task0, task1)
    system.add_task_hierarchy(task1, task2)
    system.add_task_dependency(task0, task3)

    expected_subgraph = NetworkGraph.empty()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_task(task3)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task1, task2)
    expected_subgraph.add_dependency(task0, task3)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.DependencyIntroducesDependencyDuplicationError
    ) as exc_info:
        logic_layer.create_task_dependency(task2, task3)
    assert exc_info.value.dependee_task == task2
    assert exc_info.value.dependent_task == task3
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependency_duplication_with_dependent_task_superior_task(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when their is a dependency duplication with a superior-task of the dependent-task."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task_hierarchy(task1, task2)
    system.add_task_hierarchy(task2, task3)
    system.add_task_dependency(task0, task1)

    expected_subgraph = NetworkGraph.empty()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_task(task3)
    expected_subgraph.add_hierarchy(task1, task2)
    expected_subgraph.add_hierarchy(task2, task3)
    expected_subgraph.add_dependency(task0, task1)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.DependencyIntroducesDependencyDuplicationError
    ) as exc_info:
        logic_layer.create_task_dependency(task0, task3)
    assert exc_info.value.dependee_task == task0
    assert exc_info.value.dependent_task == task3
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependency_duplication_with_superior_tasks_of_dependee_and_dependent_tasks(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when their is a dependency duplication with superior-tasks of both the dependee-task and the dependent-task."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)
    task4 = tasks.UID(4)
    task5 = tasks.UID(5)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)
    system.add_task(task5)
    system.add_task_hierarchy(task0, task1)
    system.add_task_hierarchy(task1, task2)
    system.add_task_hierarchy(task3, task4)
    system.add_task_hierarchy(task4, task5)
    system.add_task_dependency(task0, task3)

    expected_subgraph = NetworkGraph.empty()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_task(task3)
    expected_subgraph.add_task(task4)
    expected_subgraph.add_task(task5)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task1, task2)
    expected_subgraph.add_hierarchy(task3, task4)
    expected_subgraph.add_hierarchy(task4, task5)
    expected_subgraph.add_dependency(task0, task3)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.DependencyIntroducesDependencyDuplicationError
    ) as exc_info:
        logic_layer.create_task_dependency(task2, task5)
    assert exc_info.value.dependee_task == task2
    assert exc_info.value.dependent_task == task5
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependency_duplication_with_superior_tasks_of_dependee_and_dependent_tasks_and_trim(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when their is a dependency duplication with superior-tasks of both the dependee-task and the dependent-task and trim unecessary tasks."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)
    task4 = tasks.UID(4)
    task5 = tasks.UID(5)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)
    system.add_task(task5)
    system.add_task_hierarchy(task0, task1)
    system.add_task_hierarchy(task1, task2)
    system.add_task_hierarchy(task3, task4)
    system.add_task_hierarchy(task4, task5)
    system.add_task_dependency(task1, task4)

    expected_subgraph = NetworkGraph.empty()
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_task(task4)
    expected_subgraph.add_task(task5)
    expected_subgraph.add_hierarchy(task1, task2)
    expected_subgraph.add_hierarchy(task4, task5)
    expected_subgraph.add_dependency(task1, task4)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.DependencyIntroducesDependencyDuplicationError
    ) as exc_info:
        logic_layer.create_task_dependency(task2, task5)
    assert exc_info.value.dependee_task == task2
    assert exc_info.value.dependent_task == task5
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependency_duplication_with_dependee_task_inferior_task(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when their is a dependency duplication with the inferior-task of the dependee-task."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task_hierarchy(task0, task1)
    system.add_task_hierarchy(task1, task2)
    system.add_task_dependency(task2, task3)

    expected_subgraph = NetworkGraph.empty()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_task(task3)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task1, task2)
    expected_subgraph.add_dependency(task2, task3)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.DependencyIntroducesDependencyDuplicationError
    ) as exc_info:
        logic_layer.create_task_dependency(task0, task3)
    assert exc_info.value.dependee_task == task0
    assert exc_info.value.dependent_task == task3
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependency_duplication_with_dependent_task_inferior_task(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when their is a dependency duplication with an inferior-task of the dependee-task."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task_hierarchy(task1, task2)
    system.add_task_hierarchy(task2, task3)
    system.add_task_dependency(task0, task3)

    expected_subgraph = NetworkGraph.empty()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_task(task3)
    expected_subgraph.add_hierarchy(task1, task2)
    expected_subgraph.add_hierarchy(task2, task3)
    expected_subgraph.add_dependency(task0, task3)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.DependencyIntroducesDependencyDuplicationError
    ) as exc_info:
        logic_layer.create_task_dependency(task0, task1)
    assert exc_info.value.dependee_task == task0
    assert exc_info.value.dependent_task == task1
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependency_duplication_with_inferior_tasks_of_dependee_and_dependent_tasks(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when their is a dependency duplication with inferior-tasks of both the dependee-task and the dependent-task."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)
    task4 = tasks.UID(4)
    task5 = tasks.UID(5)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)
    system.add_task(task5)
    system.add_task_hierarchy(task0, task1)
    system.add_task_hierarchy(task1, task2)
    system.add_task_hierarchy(task3, task4)
    system.add_task_hierarchy(task4, task5)
    system.add_task_dependency(task2, task5)

    expected_subgraph = NetworkGraph.empty()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_task(task3)
    expected_subgraph.add_task(task4)
    expected_subgraph.add_task(task5)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task1, task2)
    expected_subgraph.add_hierarchy(task3, task4)
    expected_subgraph.add_hierarchy(task4, task5)
    expected_subgraph.add_dependency(task2, task5)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.DependencyIntroducesDependencyDuplicationError
    ) as exc_info:
        logic_layer.create_task_dependency(task0, task3)
    assert exc_info.value.dependee_task == task0
    assert exc_info.value.dependent_task == task3
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependency_duplication_with_inferior_tasks_of_dependee_and_dependent_tasks_and_trim(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when their is a dependency duplication with inferior-tasks of both the dependee-task and the dependent-task and trim unecessary tasks."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)
    task4 = tasks.UID(4)
    task5 = tasks.UID(5)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)
    system.add_task(task5)
    system.add_task_hierarchy(task0, task1)
    system.add_task_hierarchy(task1, task2)
    system.add_task_hierarchy(task3, task4)
    system.add_task_hierarchy(task4, task5)
    system.add_task_dependency(task1, task4)

    expected_subgraph = NetworkGraph.empty()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task3)
    expected_subgraph.add_task(task4)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task3, task4)
    expected_subgraph.add_dependency(task1, task4)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.DependencyIntroducesDependencyDuplicationError
    ) as exc_info:
        logic_layer.create_task_dependency(task0, task3)
    assert exc_info.value.dependee_task == task0
    assert exc_info.value.dependent_task == task3
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependency_crossover_with_dependee_task_superior_task_and_dependent_task_inferior_task(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when their is a dependency crossover with a superior-task of the dependee-task and an inferior-task of the dependent-task."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)
    task4 = tasks.UID(4)
    task5 = tasks.UID(5)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)
    system.add_task(task5)
    system.add_task_hierarchy(task0, task1)
    system.add_task_hierarchy(task1, task2)
    system.add_task_hierarchy(task3, task4)
    system.add_task_hierarchy(task4, task5)
    system.add_task_dependency(task0, task5)

    expected_subgraph = NetworkGraph.empty()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_task(task3)
    expected_subgraph.add_task(task4)
    expected_subgraph.add_task(task5)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task1, task2)
    expected_subgraph.add_hierarchy(task3, task4)
    expected_subgraph.add_hierarchy(task4, task5)
    expected_subgraph.add_dependency(task0, task5)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyIntroducesDependencyCrossoverError) as exc_info:
        logic_layer.create_task_dependency(task2, task3)
    assert exc_info.value.dependee_task == task2
    assert exc_info.value.dependent_task == task3
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependency_crossover_with_dependee_task_superior_task_and_dependent_task_inferior_task_with_trim(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when their is a dependency crossover with a superior-task of the dependee-task and an inferior-task of the dependent-task and trim excess tasks."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)
    task4 = tasks.UID(4)
    task5 = tasks.UID(5)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)
    system.add_task(task5)
    system.add_task_hierarchy(task0, task1)
    system.add_task_hierarchy(task1, task2)
    system.add_task_hierarchy(task3, task4)
    system.add_task_hierarchy(task4, task5)
    system.add_task_dependency(task1, task4)

    expected_subgraph = NetworkGraph.empty()
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_task(task3)
    expected_subgraph.add_task(task4)
    expected_subgraph.add_hierarchy(task1, task2)
    expected_subgraph.add_hierarchy(task3, task4)
    expected_subgraph.add_dependency(task1, task4)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyIntroducesDependencyCrossoverError) as exc_info:
        logic_layer.create_task_dependency(task2, task3)
    assert exc_info.value.dependee_task == task2
    assert exc_info.value.dependent_task == task3
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependency_crossover_with_dependee_task_inferior_task_and_dependent_task_superior_task(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when their is a dependency crossover with a inferior-task of the dependee-task and a superior-task of the dependent-task."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)
    task4 = tasks.UID(4)
    task5 = tasks.UID(5)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)
    system.add_task(task5)
    system.add_task_hierarchy(task0, task1)
    system.add_task_hierarchy(task1, task2)
    system.add_task_hierarchy(task3, task4)
    system.add_task_hierarchy(task4, task5)
    system.add_task_dependency(task2, task3)

    expected_subgraph = NetworkGraph.empty()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_task(task3)
    expected_subgraph.add_task(task4)
    expected_subgraph.add_task(task5)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task1, task2)
    expected_subgraph.add_hierarchy(task3, task4)
    expected_subgraph.add_hierarchy(task4, task5)
    expected_subgraph.add_dependency(task2, task3)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyIntroducesDependencyCrossoverError) as exc_info:
        logic_layer.create_task_dependency(task0, task5)
    assert exc_info.value.dependee_task == task0
    assert exc_info.value.dependent_task == task5
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependency_crossover_with_dependee_task_inferior_task_and_dependent_task_superior_task_with_trim(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_dependency method fails when their is a dependency crossover with a inferior-task of the dependee-task and a superior-task of the dependent-task and trim excess tasks."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)
    task4 = tasks.UID(4)
    task5 = tasks.UID(5)

    system = domain.System.empty()
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)
    system.add_task(task5)
    system.add_task_hierarchy(task0, task1)
    system.add_task_hierarchy(task1, task2)
    system.add_task_hierarchy(task3, task4)
    system.add_task_hierarchy(task4, task5)
    system.add_task_dependency(task1, task4)

    expected_subgraph = NetworkGraph.empty()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task4)
    expected_subgraph.add_task(task5)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task4, task5)
    expected_subgraph.add_dependency(task1, task4)

    data_layer_mock.load_system.return_value = system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyIntroducesDependencyCrossoverError) as exc_info:
        logic_layer.create_task_dependency(task0, task5)
    assert exc_info.value.dependee_task == task0
    assert exc_info.value.dependent_task == task5
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@pytest.mark.parametrize(
    "started_progress",
    [tasks.Progress.IN_PROGRESS, tasks.Progress.COMPLETED],
)
@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_success_completed_dependee_task_started_dependent_task(
    data_layer_mock: mock.MagicMock, started_progress: tasks.Progress
) -> None:
    """Test the create_dependency method succeeds when the dependee-task is completed and the dependent-task is started."""
    dependent_task = tasks.UID(0)
    dependee_task = tasks.UID(1)
    system = domain.System.empty()

    system.add_task(dependee_task)
    system.add_task(dependent_task)
    system.set_task_progress(dependee_task, tasks.Progress.COMPLETED)
    system.set_task_progress(dependent_task, started_progress)

    system_with_dependency = copy.deepcopy(system)
    system_with_dependency.add_task_dependency(dependee_task, dependent_task)

    data_layer_mock.load_system.return_value = system
    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.create_task_dependency(dependee_task, dependent_task)

    data_layer_mock.load_system.assert_called_once()
    data_layer_mock.save_system.assert_called_once_with(system_with_dependency)


@pytest.mark.parametrize(
    "incomplete_progress",
    [tasks.Progress.NOT_STARTED, tasks.Progress.IN_PROGRESS],
)
@pytest.mark.parametrize(
    "started_progress",
    [tasks.Progress.IN_PROGRESS, tasks.Progress.COMPLETED],
)
@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_incomplete_dependee_task_started_dependent_task(
    data_layer_mock: mock.MagicMock,
    started_progress: tasks.Progress,
    incomplete_progress: tasks.Progress,
) -> None:
    """Test the create_dependency method fails when the dependee-task is incomplete and the dependent-task is started."""
    dependent_task = tasks.UID(0)
    dependee_task = tasks.UID(1)
    system = domain.System.empty()

    system.add_task(dependee_task)
    system.add_task(dependent_task)
    system.set_task_progress(dependee_task, incomplete_progress)
    system.set_task_progress(dependent_task, started_progress)

    data_layer_mock.load_system.return_value = system
    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependeeIncompleteDependentStartedError) as exc_info:
        logic_layer.create_task_dependency(dependee_task, dependent_task)
    assert exc_info.value.dependee_task == dependee_task
    assert exc_info.value.dependent_task == dependent_task
    assert exc_info.value.dependee_progress == incomplete_progress
    assert exc_info.value.dependent_progress == started_progress

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False
