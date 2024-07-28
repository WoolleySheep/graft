"""Unit tests for `System.create_hierarchy`."""

import copy
import itertools
from unittest import mock

import pytest

from graft import domain
from graft.domain import tasks
from graft.standard import standard


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_success(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method works as expected."""
    supertask = tasks.UID(0)
    subtask = tasks.UID(1)

    system = empty_system
    system.add_task(supertask)
    system.add_task(subtask)

    system_with_hierarchy = copy.deepcopy(system)
    system_with_hierarchy.add_task_hierarchy(supertask, subtask)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.create_task_hierarchy(supertask=supertask, subtask=subtask)

    data_layer_mock.load_system.assert_called_once()
    data_layer_mock.save_system.assert_called_once_with(system_with_hierarchy)


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_supertask_not_exist(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when the supertask does not exist."""
    supertask = tasks.UID(0)
    subtask = tasks.UID(1)
    absent_supertask = tasks.UID(2)

    system = empty_system
    system.add_task(supertask)
    system.add_task(subtask)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.TaskDoesNotExistError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=absent_supertask, subtask=subtask)
    assert exc_info.value.task == absent_supertask

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_subtask_not_exist(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when the subtask does not exist."""
    supertask = tasks.UID(0)
    subtask = tasks.UID(1)
    absent_subtask = tasks.UID(2)

    system = empty_system
    system.add_task(supertask)
    system.add_task(subtask)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.TaskDoesNotExistError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=supertask, subtask=absent_subtask)
    assert exc_info.value.task == absent_subtask

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_supertask_subtask_the_same(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when the supertask and subtask are the same."""
    task = tasks.UID(0)

    system = empty_system
    system.add_task(task)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyLoopError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task, subtask=task)
    assert exc_info.value.task == task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_hierarchy_already_exists(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when the hierarchy already exists."""
    supertask = tasks.UID(0)
    subtask = tasks.UID(1)

    system = empty_system
    system.add_task(supertask)
    system.add_task(subtask)
    system.add_task_hierarchy(supertask=supertask, subtask=subtask)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyAlreadyExistsError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=supertask, subtask=subtask)
    assert exc_info.value.supertask == supertask
    assert exc_info.value.subtask == subtask

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_inverse_hierarchy_already_exists(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when an inverse hierarchy already exists."""
    supertask = tasks.UID(0)
    subtask = tasks.UID(1)

    system = empty_system
    system.add_task(supertask)
    system.add_task(subtask)
    system.add_task_hierarchy(supertask=supertask, subtask=subtask)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(supertask)
    expected_subgraph.add_task(subtask)
    expected_subgraph.add_hierarchy(supertask, subtask)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyIntroducesCycleError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=subtask, subtask=supertask)
    assert exc_info.value.supertask == subtask
    assert exc_info.value.subtask == supertask
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_introduces_cycle(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when it introduces a cycle."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system = empty_system
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

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyIntroducesCycleError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task2, subtask=task0)
    assert exc_info.value.supertask == task2
    assert exc_info.value.subtask == task0
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_introduces_cycle_prunes_subgraph_correctly(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when it introduces a cycle and.

    prunes the connecting subgraph of irrelevant nodes.
    """
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task_hierarchy(supertask=task0, subtask=task1)
    system.add_task_hierarchy(supertask=task1, subtask=task2)
    system.add_task_hierarchy(supertask=task1, subtask=task3)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task1, task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyIntroducesCycleError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task2, subtask=task0)
    assert exc_info.value.supertask == task2
    assert exc_info.value.subtask == task0
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_path_already_exists_from_supertask_to_subtask(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when a path already exists from.

    the supertask to the subtask.
    """
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system = empty_system
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

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyIntroducesRedundantHierarchyError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task0, subtask=task2)
    assert exc_info.value.supertask == task0
    assert exc_info.value.subtask == task2
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_path_already_exists_from_supertask_to_subtask_and_prunes_subgraph_correctly(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when a path already exists from.

    the supertask to the subtask and prunes the connecting subgraph of
    irrelevant tasks.
    """
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task_hierarchy(supertask=task0, subtask=task1)
    system.add_task_hierarchy(supertask=task1, subtask=task2)
    system.add_task_hierarchy(supertask=task1, subtask=task3)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task1, task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyIntroducesRedundantHierarchyError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task0, subtask=task2)
    assert exc_info.value.supertask == task0
    assert exc_info.value.subtask == task2
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_subtask_is_already_subtask_of_superior_task_of_supertask(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when the subtask is already a.

    subtask of a superior-task of the supertask.
    """
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task_hierarchy(supertask=task0, subtask=task1)
    system.add_task_hierarchy(supertask=task0, subtask=task2)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task0, task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyIntroducesRedundantHierarchyError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task1, subtask=task2)
    assert exc_info.value.supertask == task1
    assert exc_info.value.subtask == task2
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_subtask_is_already_subtask_of_superior_task_of_supertask_and_prunes_subgraph_correctly(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when the subtask is already a.

    subtask of a superior-task of the supertask and prunes the connecting
    subgraph of irrelevant tasks.
    """
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task_hierarchy(supertask=task0, subtask=task1)
    system.add_task_hierarchy(supertask=task0, subtask=task2)
    system.add_task_hierarchy(supertask=task3, subtask=task1)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task0, task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyIntroducesRedundantHierarchyError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task1, subtask=task2)
    assert exc_info.value.supertask == task1
    assert exc_info.value.subtask == task2
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_supertask_is_already_supertask_of_inferior_task_of_subtask(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_hierarchy method fails when the supertask is already a supertask of an inferior task of the subtask."""
    system = domain.System.empty()
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task_hierarchy(task0, task2)
    system.add_task_hierarchy(task1, task2)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_hierarchy(task0, task2)
    expected_subgraph.add_hierarchy(task1, task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyIntroducesRedundantHierarchyError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task0, subtask=task1)
    assert exc_info.value.supertask == task0
    assert exc_info.value.subtask == task1
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_supertask_is_already_supertask_of_inferior_task_of_subtask_and_prunes_subgraph_correctly(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the create_hierarchy method fails when the supertask is already a.

    supertask of an inferior task of the subtask and prunes the connecting
    subgraph of irrelevant tasks.
    """
    system = domain.System.empty()
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)

    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task_hierarchy(task0, task2)
    system.add_task_hierarchy(task1, task2)
    system.add_task_hierarchy(task0, task3)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_hierarchy(task0, task2)
    expected_subgraph.add_hierarchy(task1, task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyIntroducesRedundantHierarchyError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task0, subtask=task1)
    assert exc_info.value.supertask == task0
    assert exc_info.value.subtask == task1
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_dependency_path_from_supertask_to_subtask(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when a dependency path already.

    exists from the supertask to the subtask.
    """
    supertask = tasks.UID(0)
    subtask = tasks.UID(1)

    system = empty_system
    system.add_task(supertask)
    system.add_task(subtask)
    system.add_task_dependency(dependee_task=supertask, dependent_task=subtask)

    expected_subgraph = tasks.DependencyGraph()
    expected_subgraph.add_task(supertask)
    expected_subgraph.add_task(subtask)
    expected_subgraph.add_dependency(supertask, subtask)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.DependencyPathAlreadyExistsFromSuperTaskToSubTaskError
    ) as exc_info:
        logic_layer.create_task_hierarchy(supertask=supertask, subtask=subtask)
    assert exc_info.value.supertask == supertask
    assert exc_info.value.subtask == subtask
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_dependency_path_from_subtask_to_supertask(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when a dependency path already.

    exists from the subtask to the supertask.
    """
    supertask = tasks.UID(0)
    subtask = tasks.UID(1)

    system = empty_system
    system.add_task(supertask)
    system.add_task(subtask)
    system.add_task_dependency(dependee_task=subtask, dependent_task=supertask)

    expected_subgraph = tasks.DependencyGraph()
    expected_subgraph.add_task(supertask)
    expected_subgraph.add_task(subtask)
    expected_subgraph.add_dependency(subtask, supertask)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.DependencyPathAlreadyExistsFromSubTaskToSuperTaskError
    ) as exc_info:
        logic_layer.create_task_hierarchy(supertask=supertask, subtask=subtask)
    assert exc_info.value.supertask == supertask
    assert exc_info.value.subtask == subtask
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_stream_path_from_supertask_to_subtask(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when a stream path already exists.

    from the supertask to the subtask.
    """
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task_dependency(dependee_task=task0, dependent_task=task1)
    system.add_task_hierarchy(supertask=task1, subtask=task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.StreamPathFromSuperTaskToSubTaskExistsError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task0, subtask=task2)
    assert exc_info.value.supertask == task0
    assert exc_info.value.subtask == task2

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_stream_path_from_subtask_to_supertask(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when a stream path already exists.

    from the subtask to the supertask.
    """
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task_dependency(dependee_task=task0, dependent_task=task1)
    system.add_task_hierarchy(supertask=task1, subtask=task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.StreamPathFromSubTaskToSuperTaskExistsError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task2, subtask=task0)
    assert exc_info.value.supertask == task2
    assert exc_info.value.subtask == task0

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_stream_path_from_supertask_to_inferior_task_of_subtask(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when a stream path already exists.

    from the supertask to an inferior-task of the subtask.
    """
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task_dependency(dependee_task=task0, dependent_task=task1)
    system.add_task_hierarchy(supertask=task2, subtask=task1)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.StreamPathFromSuperTaskToInferiorTaskOfSubTaskExistsError
    ) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task0, subtask=task2)
    assert exc_info.value.supertask == task0
    assert exc_info.value.subtask == task2

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_stream_path_from_inferior_task_of_subtask_to_supertask(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when a stream path already exists.

    from an inferior-task of the subtask to the supertask.
    """
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)

    system.add_task_hierarchy(supertask=task0, subtask=task1)
    system.add_task_hierarchy(supertask=task1, subtask=task2)
    system.add_task_dependency(dependee_task=task2, dependent_task=task3)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.StreamPathFromInferiorTaskOfSubTaskToSuperTaskExistsError
    ) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task3, subtask=task0)
    assert exc_info.value.supertask == task3
    assert exc_info.value.subtask == task0

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_dependency_clash(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when a dependency clash exists."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)

    system.add_task_hierarchy(supertask=task0, subtask=task1)
    system.add_task_dependency(dependee_task=task0, dependent_task=task2)
    system.add_task_dependency(dependee_task=task1, dependent_task=task3)

    data_layer_mock.load_system.return_value = system
    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyIntroducesDependencyClashError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task2, subtask=task3)
    assert exc_info.value.supertask == task2
    assert exc_info.value.subtask == task3

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@pytest.mark.parametrize("topside_task", [tasks.UID(0), tasks.UID(1), tasks.UID(2)])
@pytest.mark.parametrize("bottomside_task", [tasks.UID(3), tasks.UID(4), tasks.UID(5)])
@pytest.mark.parametrize(
    ("topside_task_importance", "bottomside_task_importance"),
    itertools.combinations(iterable=tasks.Importance, r=2),
)
@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_supertask_and_subtask_both_have_importance(
    data_layer_mock: mock.MagicMock,
    topside_task_importance: tasks.Importance,
    bottomside_task_importance: tasks.Importance,
    bottomside_task: tasks.UID,
    topside_task: tasks.UID,
) -> None:
    """Test that create_hierarchy fails when the topside task and the bottomside task both have importance."""
    superior_task_of_supertask = tasks.UID(0)
    supertask_of_supertask = tasks.UID(1)
    supertask = tasks.UID(2)
    subtask = tasks.UID(3)
    subtask_of_subtask = tasks.UID(4)
    inferior_task_of_subtask = tasks.UID(5)
    system = domain.System.empty()

    system.add_task(superior_task_of_supertask)
    system.add_task(supertask_of_supertask)
    system.add_task(supertask)
    system.add_task(subtask)
    system.add_task(subtask_of_subtask)
    system.add_task(inferior_task_of_subtask)
    system.add_task_hierarchy(
        supertask=superior_task_of_supertask, subtask=supertask_of_supertask
    )
    system.add_task_hierarchy(supertask=supertask_of_supertask, subtask=supertask)
    system.add_task_hierarchy(supertask=subtask, subtask=subtask_of_subtask)
    system.add_task_hierarchy(
        supertask=subtask_of_subtask, subtask=inferior_task_of_subtask
    )
    system.set_task_importance(task=topside_task, importance=topside_task_importance)
    system.set_task_importance(
        task=bottomside_task, importance=bottomside_task_importance
    )

    data_layer_mock.load_system.return_value = system
    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.MultipleImportancesInHierarchyError):
        logic_layer.create_task_hierarchy(supertask=supertask, subtask=subtask)

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_incomplete_dependee_tasks_of_supertask(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test that create_hierarchy fails when the subtask is started and a dependee task of the supertask is incomplete."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    system = domain.System.empty()

    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task_dependency(dependee_task=task0, dependent_task=task1)
    system.set_task_progress(task=task2, progress=tasks.Progress.IN_PROGRESS)

    data_layer_mock.load_system.return_value = system
    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.IncompleteDependeeTasksOfSupertaskError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task1, subtask=task2)
    assert exc_info.value.supertask == task1
    assert exc_info.value.subtask == task2
    assert exc_info.value.incomplete_dependee_tasks_of_supertask_with_progress == [
        (task0, tasks.Progress.NOT_STARTED)
    ]

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_incomplete_dependee_tasks_of_superior_task_of_supertask(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test that create_hierarchy fails when the subtask is started and a dependee task of the superior task of the supertask is incomplete."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)
    system = domain.System.empty()

    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task_hierarchy(supertask=task0, subtask=task1)
    system.add_task_dependency(dependee_task=task2, dependent_task=task0)
    system.set_task_progress(task=task3, progress=tasks.Progress.IN_PROGRESS)

    data_layer_mock.load_system.return_value = system
    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.IncompleteDependeeTasksOfSuperiorTasksOfSupertaskError
    ) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task1, subtask=task3)
    assert exc_info.value.supertask == task1
    assert exc_info.value.subtask == task3

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_started_dependent_tasks_of_supertask(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test that create_hierarchy fails when the subtask is incomplete and a dependent task of the supertask is started."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    system = domain.System.empty()

    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task_dependency(dependee_task=task0, dependent_task=task1)
    system.set_task_progress(task=task0, progress=tasks.Progress.COMPLETED)
    system.set_task_progress(task=task1, progress=tasks.Progress.IN_PROGRESS)

    data_layer_mock.load_system.return_value = system
    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.StartedDependentTasksOfSupertaskError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task0, subtask=task2)
    assert exc_info.value.supertask == task0
    assert exc_info.value.subtask == task2
    assert exc_info.value.started_dependent_tasks_of_supertask_with_progress == [
        (task1, tasks.Progress.IN_PROGRESS)
    ]

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_started_dependent_tasks_of_superior_tasks_of_supertask(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test that create_hierarchy fails when the subtask is incomplete and a dependent task of the superior tasks of the supertask is started."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)
    system = domain.System.empty()

    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task_hierarchy(supertask=task0, subtask=task1)
    system.add_task_dependency(dependee_task=task0, dependent_task=task2)
    system.set_task_progress(task=task1, progress=tasks.Progress.COMPLETED)
    system.set_task_progress(task=task2, progress=tasks.Progress.IN_PROGRESS)

    data_layer_mock.load_system.return_value = system
    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.StartedDependentTasksOfSuperiorTasksOfSupertaskError
    ) as exc_info:
        logic_layer.create_task_hierarchy(supertask=task1, subtask=task3)
    assert exc_info.value.supertask == task1
    assert exc_info.value.subtask == task3

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_success_concrete_supertask(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test that create_hierarchy succeeds when the supertask is concrete.

    Ensures that the supertask progress is erased as expected.
    """
    supertask = tasks.UID(0)
    subtask = tasks.UID(1)
    system = domain.System.empty()

    system.add_task(supertask)
    system.add_task(subtask)
    assert (
        system.task_system().attributes_register()[supertask].progress
        is tasks.Progress.NOT_STARTED
    )

    system_with_hierarchy = copy.deepcopy(system)
    system_with_hierarchy.add_task_hierarchy(supertask=supertask, subtask=subtask)

    assert (
        system_with_hierarchy.task_system().attributes_register()[supertask].progress
        is None
    )

    data_layer_mock.load_system.return_value = system
    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.create_task_hierarchy(supertask=supertask, subtask=subtask)

    data_layer_mock.load_system.assert_called_once()
    data_layer_mock.save_system.assert_called_once_with(system_with_hierarchy)


@pytest.mark.parametrize(
    ("supertask_progress", "subtask_progress"),
    itertools.combinations(iterable=tasks.Progress, r=2),
)
@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_concrete_supertask_differing_progress(
    data_layer_mock: mock.MagicMock,
    supertask_progress: tasks.Progress,
    subtask_progress: tasks.Progress,
) -> None:
    """Test that create_hierarchy fails when the supertask is concrete and the progress of supertask and subtask differ."""
    supertask = tasks.UID(0)
    subtask = tasks.UID(1)
    system = domain.System.empty()

    system.add_task(supertask)
    system.add_task(subtask)
    system.set_task_progress(supertask, supertask_progress)
    system.set_task_progress(subtask, subtask_progress)

    data_layer_mock.load_system.return_value = system
    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.MismatchedProgressForNewSupertaskError) as exc_info:
        logic_layer.create_task_hierarchy(supertask=supertask, subtask=subtask)
    assert exc_info.value.supertask == supertask
    assert exc_info.value.supertask_progress == supertask_progress
    assert exc_info.value.subtask == subtask
    assert exc_info.value.subtask_progress == subtask_progress

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False
