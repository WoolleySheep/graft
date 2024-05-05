"""Unit tests for Standard.update_task_description."""

import copy
from unittest import mock

import pytest

from graft import domain, standard
from graft.domain import tasks


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_description_success_with_description(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the update_task_description method works when given a description."""
    task = tasks.UID(0)
    description = tasks.Description("Hello world")

    system_with_one_undescribed_task = empty_system
    system_with_one_undescribed_task.add_task(task)

    system_with_one_described_task = copy.deepcopy(system_with_one_undescribed_task)
    system_with_one_described_task.set_task_description(
        task=task, description=description
    )

    data_layer_mock.load_system.return_value = system_with_one_undescribed_task

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.update_task_description(task=task, description=description)

    data_layer_mock.load_system.assert_called_once_with()
    data_layer_mock.save_system.assert_called_once_with(system_with_one_described_task)


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_description_success_with_none(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the update_task_description method works when given no description."""
    task = tasks.UID(0)
    description = tasks.Description("Hello world")

    system_with_one_undescribed_task = empty_system
    system_with_one_undescribed_task.add_task(task)

    system_with_one_described_task = copy.deepcopy(system_with_one_undescribed_task)
    system_with_one_described_task.set_task_description(
        task=task, description=description
    )

    data_layer_mock.load_system.return_value = system_with_one_described_task

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.update_task_description(task=task, description=None)

    data_layer_mock.load_system.assert_called_once_with()
    data_layer_mock.save_system.assert_called_once_with(
        system_with_one_undescribed_task
    )


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_description_failure_task_does_not_exist(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the update_task_description method fails when the task does not exist."""
    task = tasks.UID(0)

    data_layer_mock.load_system.return_value = empty_system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.TaskDoesNotExistError) as e:
        logic_layer.update_task_description(task=task, description=None)
    assert e.value.task == task

    data_layer_mock.load_system.assert_called_once_with()
    data_layer_mock.save_system.assert_not_called()
