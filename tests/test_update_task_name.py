"""Unit tests for logic.update_task_name."""

import copy
from unittest import mock

import pytest

from graft import domain
from graft.domain import tasks
from graft.layers import logic


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_name_success_with_name(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the update_task_name method works when given a name."""
    task = tasks.UID(0)
    name = tasks.Name("Hello world")

    system_with_one_task = empty_system
    system_with_one_task.add_task(task)

    system_with_one_named_task = copy.deepcopy(system_with_one_task)
    system_with_one_named_task.set_task_name(task=task, name=name)

    data_layer_mock.load_system.return_value = system_with_one_task

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.update_task_name(task=task, name=name)

    data_layer_mock.load_system.assert_called_once_with()
    data_layer_mock.save_system.assert_called_once_with(system_with_one_named_task)


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_name_success_with_none(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the update_task_name method works when given no name."""
    task = tasks.UID(0)
    name = tasks.Name("Hello world")

    system_with_one_unnamed_task = empty_system
    system_with_one_unnamed_task.add_task(task)

    system_with_one_named_task = copy.deepcopy(system_with_one_unnamed_task)
    system_with_one_named_task.set_task_name(task=task, name=name)

    data_layer_mock.load_system.return_value = system_with_one_named_task

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.update_task_name(task=task, name=tasks.Name())

    data_layer_mock.load_system.assert_called_once_with()
    data_layer_mock.save_system.assert_called_once_with(system_with_one_unnamed_task)


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_name_failure_task_does_not_exist(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the update_task_name method fails when the task does not exist."""
    task = tasks.UID(0)

    data_layer_mock.load_system.return_value = empty_system

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.TaskDoesNotExistError) as e:
        logic_layer.update_task_name(task=task, name=tasks.Name())
    assert e.value.task == task

    data_layer_mock.load_system.assert_called_once_with()
    data_layer_mock.save_system.assert_not_called()
