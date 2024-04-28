"""Unit tests for `System.delete_dependency`."""

import copy
from unittest import mock

import pytest

from graft import domain
from graft.domain import tasks
from graft.standard import standard


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_dependency_success(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the delete_dependency method succeeds as expected."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)

    system = empty_system
    system.add_task(dependee_task)
    system.add_task(dependent_task)

    system_without_dependency = copy.deepcopy(system)

    system.add_dependency(dependee_task, dependent_task)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.delete_dependency(dependee_task, dependent_task)

    data_layer_mock.load_system.assert_called_once()
    data_layer_mock.save_system.assert_called_once_with(system_without_dependency)


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_dependency_failure_dependee_task_not_exists(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the delete_dependency method fails when the dependee task does not exist."""
    absent_dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)

    system = empty_system
    system.add_task(dependent_task)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.TaskDoesNotExistError) as exc_info:
        logic_layer.delete_hierarchy(absent_dependee_task, dependent_task)
    assert exc_info.value.task == absent_dependee_task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_dependency_failure_dependent_task_not_exists(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the delete_dependency method fails when the dependent task does not exist."""
    dependee_task = tasks.UID(0)
    absent_dependent_task = tasks.UID(1)

    system = empty_system
    system.add_task(dependee_task)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.TaskDoesNotExistError) as exc_info:
        logic_layer.delete_hierarchy(dependee_task, absent_dependent_task)
    assert exc_info.value.task == absent_dependent_task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_dependency_failure_dependency_loop(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the delete_dependency method fails when a dependency loop occurs."""
    task = tasks.UID(0)

    system = empty_system
    system.add_task(task)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyLoopError) as exc_info:
        logic_layer.delete_dependency(task, task)
    assert exc_info.value.task == task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_dependency_failure_dependency_not_exist(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the delete_dependency method fails when the dependency does not exist."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)

    system = empty_system
    system.add_task(dependee_task)
    system.add_task(dependent_task)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyDoesNotExistError) as exc_info:
        logic_layer.delete_dependency(dependee_task, dependent_task)
    assert exc_info.value.dependee_task == dependee_task
    assert exc_info.value.dependent_task == dependent_task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False
