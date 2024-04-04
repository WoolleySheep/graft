import copy
from unittest import mock

import pytest

from graft import domain
from graft.domain import tasks
from graft.standard import standard


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_hierarchy_success(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the delete_hierarchy method succeeds as expected."""
    supertask = tasks.UID(0)
    subtask = tasks.UID(1)

    system = empty_system
    system.add_task(supertask)
    system.add_task(subtask)

    system_without_hierarchy = copy.deepcopy(system)

    system.add_hierarchy(supertask, subtask)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.delete_hierarchy(supertask, subtask)

    data_layer_mock.load_system.assert_called_once()
    data_layer_mock.save_system.assert_called_once_with(system_without_hierarchy)


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_hierarchy_failure_supertask_not_exist(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the delete_hierarchy method fails when the supertask does not exist."""
    absent_supertask = tasks.UID(0)
    subtask = tasks.UID(1)

    system = empty_system
    system.add_task(subtask)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.TaskDoesNotExistError) as exc_info:
        logic_layer.delete_hierarchy(absent_supertask, subtask)
    assert exc_info.value.task == absent_supertask

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_hierarchy_failure_subtask_not_exist(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the delete_hierarchy method fails when the subtask does not exist."""
    supertask = tasks.UID(0)
    absent_subtask = tasks.UID(1)

    system = empty_system
    system.add_task(supertask)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.TaskDoesNotExistError) as exc_info:
        logic_layer.delete_hierarchy(supertask, absent_subtask)
    assert exc_info.value.task == absent_subtask

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_hierarchy_failure_hierarchy_loop(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the delete_hierarchy method fails when a hierarchy loop occurs."""
    task = tasks.UID(0)

    system = empty_system
    system.add_task(task)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyLoopError) as exc_info:
        logic_layer.delete_hierarchy(task, task)
    assert exc_info.value.task == task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_hierarchy_failure_hierarchy_not_exist(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the delete_hierarchy method fails when the hierarchy does not exist."""
    supertask = tasks.UID(0)
    subtask = tasks.UID(1)

    system = empty_system
    system.add_task(supertask)
    system.add_task(subtask)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HierarchyDoesNotExistError) as exc_info:
        logic_layer.delete_hierarchy(supertask, subtask)
    assert exc_info.value.supertask == supertask
    assert exc_info.value.subtask == subtask

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False
