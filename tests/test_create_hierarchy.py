import copy
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
    system_with_hierarchy.add_hierarchy(supertask, subtask)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.create_hierarchy(supertask=supertask, subtask=subtask)

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
        logic_layer.create_hierarchy(supertask=absent_supertask, subtask=subtask)
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
        logic_layer.create_hierarchy(supertask=supertask, subtask=absent_subtask)
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
        logic_layer.create_hierarchy(supertask=task, subtask=task)
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
    system.add_hierarchy(supertask=supertask, subtask=subtask)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyAlreadyExistsError) as exc_info:
        logic_layer.create_hierarchy(supertask=supertask, subtask=subtask)
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
    system.add_hierarchy(supertask=subtask, subtask=supertask)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.InverseHierarchyAlreadyExistsError) as exc_info:
        logic_layer.create_hierarchy(supertask=supertask, subtask=subtask)
    assert exc_info.value.supertask == supertask
    assert exc_info.value.subtask == subtask

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
    system.add_hierarchy(supertask=task0, subtask=task1)
    system.add_hierarchy(supertask=task1, subtask=task2)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task1, task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyIntroducesCycleError) as exc_info:
        logic_layer.create_hierarchy(supertask=task2, subtask=task0)
    assert exc_info.value.supertask == task2
    assert exc_info.value.subtask == task0
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_introduces_cycle_prunes_subgraph_correctly(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when it introduces a cycle and
    prunes the connecting subgraph of irrelevant nodes."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_hierarchy(supertask=task0, subtask=task1)
    system.add_hierarchy(supertask=task1, subtask=task2)
    system.add_hierarchy(supertask=task1, subtask=task3)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task1, task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyIntroducesCycleError) as exc_info:
        logic_layer.create_hierarchy(supertask=task2, subtask=task0)
    assert exc_info.value.supertask == task2
    assert exc_info.value.subtask == task0
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_path_already_exists_from_supertask_to_subtask(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when a path already exists from
    the supertask to the subtask."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_hierarchy(supertask=task0, subtask=task1)
    system.add_hierarchy(supertask=task1, subtask=task2)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task1, task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyPathAlreadyExistsError) as exc_info:
        logic_layer.create_hierarchy(supertask=task0, subtask=task2)
    assert exc_info.value.supertask == task0
    assert exc_info.value.subtask == task2
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_path_already_exists__from_supertask_to_subtask_and_prunes_subgraph_correctly(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when a path already exists from
    the supertask to the subtask and prunes the connecting subgraph of
    irrelevant tasks."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_hierarchy(supertask=task0, subtask=task1)
    system.add_hierarchy(supertask=task1, subtask=task2)
    system.add_hierarchy(supertask=task1, subtask=task3)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_hierarchy(task0, task1)
    expected_subgraph.add_hierarchy(task1, task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyPathAlreadyExistsError) as exc_info:
        logic_layer.create_hierarchy(supertask=task0, subtask=task2)
    assert exc_info.value.supertask == task0
    assert exc_info.value.subtask == task2
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False

@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_subtask_is_already_subtask_of_superior_task_of_supertask(
            data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when the subtask is already a
    subtask of a superior-task of the supertask."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_hierarchy(supertask=task0, subtask=task1)
    system.add_hierarchy(supertask=task0, subtask=task2)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_hierarchy(task0, task1)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.SubTaskIsAlreadySubTaskOfSuperiorTaskOfSuperTaskError) as exc_info:
        logic_layer.create_hierarchy(supertask=task1, subtask=task2)
    assert exc_info.value.supertask == task1
    assert exc_info.value.subtask == task2
    assert exc_info.value.subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False

@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_hierarchy_failure_subtask_is_already_subtask_of_superior_task_of_supertask_and_prunes_subgraph_correctly(
            data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_hierarchy method fails when the subtask is already a
    subtask of a superior-task of the supertask and prunes the connecting
    subgraph of irrelevant tasks."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_hierarchy(supertask=task0, subtask=task1)
    system.add_hierarchy(supertask=task0, subtask=task2)
    system.add_hierarchy(supertask=task3, subtask=task1)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_hierarchy(task0, task1)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.SubTaskIsAlreadySubTaskOfSuperiorTaskOfSuperTaskError) as exc_info:
        logic_layer.create_hierarchy(supertask=task1, subtask=task2)
    assert exc_info.value.supertask == task1
    assert exc_info.value.subtask == task2
    assert exc_info.value.subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False