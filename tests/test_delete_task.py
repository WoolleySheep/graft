"""Unit tests for `System.delete_task`."""

from unittest import mock

import pytest

from graft import domain
from graft.domain import tasks
from graft.layers import logic


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_task_success(data_layer_mock: mock.MagicMock) -> None:
    """Test the delete_task method works as expected."""
    task = tasks.UID(0)
    empty_system = domain.System.empty()

    system_with_one_task = domain.System.empty()
    system_with_one_task.add_task(task)

    data_layer_mock.load_system.return_value = system_with_one_task

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.delete_task(task)

    data_layer_mock.load_system.assert_called_once()
    data_layer_mock.save_system.assert_called_once_with(empty_system)


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_task_failure_task_not_exist(data_layer_mock: mock.MagicMock) -> None:
    """Test the delete_task method fails when a task does not exist."""
    task = tasks.UID(0)
    empty_system = domain.System.empty()

    data_layer_mock.load_system.return_value = empty_system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.TaskDoesNotExistError) as exc_info:
        logic_layer.delete_task(task)
    assert exc_info.value.task == task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_task_failure_has_supertask(data_layer_mock: mock.MagicMock) -> None:
    """Test the delete_task method fails when task has a super-task."""
    supertask = tasks.UID(0)
    subtask = tasks.UID(1)

    system_with_hierarchy = domain.System.empty()
    system_with_hierarchy.add_task(supertask)
    system_with_hierarchy.add_task(subtask)
    system_with_hierarchy.add_task_hierarchy(supertask=supertask, subtask=subtask)

    data_layer_mock.load_system.return_value = system_with_hierarchy

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HasNeighboursError) as exc_info:
        logic_layer.delete_task(subtask)
    assert exc_info.value.task == subtask
    assert exc_info.value.supertasks == {supertask}

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_task_failure_has_subtask(data_layer_mock: mock.MagicMock) -> None:
    """Test the delete_task method fails when task has a sub-task."""
    supertask = tasks.UID(0)
    subtask = tasks.UID(1)

    system_with_hierarchy = domain.System.empty()
    system_with_hierarchy.add_task(supertask)
    system_with_hierarchy.add_task(subtask)
    system_with_hierarchy.add_task_hierarchy(supertask=supertask, subtask=subtask)

    data_layer_mock.load_system.return_value = system_with_hierarchy

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HasNeighboursError) as exc_info:
        logic_layer.delete_task(supertask)
    assert exc_info.value.task == supertask
    assert exc_info.value.subtasks == {subtask}

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_task_failure_has_dependee_task(data_layer_mock: mock.MagicMock) -> None:
    """Test the delete_task method fails when task has a dependee-task."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)

    system_with_dependency = domain.System.empty()
    system_with_dependency.add_task(dependee_task)
    system_with_dependency.add_task(dependent_task)
    system_with_dependency.add_task_dependency(
        dependee_task=dependee_task, dependent_task=dependent_task
    )

    data_layer_mock.load_system.return_value = system_with_dependency

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HasNeighboursError) as exc_info:
        logic_layer.delete_task(dependent_task)
    assert exc_info.value.task == dependent_task
    assert exc_info.value.dependee_tasks == {dependee_task}

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_task_failure_has_dependent_task(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the delete_task method fails when task has a dependent-task."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)

    system_with_dependency = domain.System.empty()
    system_with_dependency.add_task(dependee_task)
    system_with_dependency.add_task(dependent_task)
    system_with_dependency.add_task_dependency(
        dependee_task=dependee_task, dependent_task=dependent_task
    )

    data_layer_mock.load_system.return_value = system_with_dependency

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HasNeighboursError) as exc_info:
        logic_layer.delete_task(dependee_task)
    assert exc_info.value.task == dependee_task
    assert exc_info.value.dependent_tasks == {dependent_task}

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False
