"""Unit tests for Standard.update_task_description."""

import copy
from unittest import mock

import pytest

from graft import domain, standard
from graft.domain import tasks


@pytest.mark.parametrize(
    "old_progress",
    [tasks.Progress.NOT_STARTED, tasks.Progress.IN_PROGRESS, tasks.Progress.COMPLETED],
)
@pytest.mark.parametrize(
    "new_progress",
    [tasks.Progress.NOT_STARTED, tasks.Progress.IN_PROGRESS, tasks.Progress.COMPLETED],
)
@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_progress_success_one_task(
    data_layer_mock: mock.MagicMock,
    new_progress: tasks.Progress,
    old_progress: tasks.Progress,
) -> None:
    """Test that update_task_progress works for a single task."""
    task = tasks.UID(0)

    system = domain.System.empty()
    system.add_task(task)

    system_with_old_progress = copy.deepcopy(system)
    system_with_old_progress.set_task_progress(task=task, progress=old_progress)

    system_with_new_progress = copy.deepcopy(system)
    system_with_new_progress.set_task_progress(task=task, progress=new_progress)

    data_layer_mock.load_system.return_value = system_with_old_progress

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.update_task_progress(task=task, progress=new_progress)

    data_layer_mock.load_system.assert_called_once_with()
    data_layer_mock.save_system.assert_called_once_with(system_with_new_progress)


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_progress_failure_task_does_not_exist(
    data_layer_mock: mock.MagicMock,
) -> None:
    task = tasks.UID(0)
    data_layer_mock.load_system.return_value = domain.System.empty()
    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.TaskDoesNotExistError) as e:
        logic_layer.update_task_progress(task=task, progress=tasks.Progress.COMPLETED)
    assert e.value.task == task

    data_layer_mock.load_system.assert_called_once_with()
    data_layer_mock.save_system.assert_not_called()


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_progress_failure_task_is_not_concrete(
    data_layer_mock: mock.MagicMock,
) -> None:
    assert True is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_progress_failure_started_dependent_tasks(
    data_layer_mock: mock.MagicMock,
) -> None:
    assert True is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_progress_failure_started_dependent_tasks_of_superior_tasks(
    data_layer_mock: mock.MagicMock,
) -> None:
    assert True is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_progress_failure_incomplete_dependee_tasks(
    data_layer_mock: mock.MagicMock,
) -> None:
    assert True is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_progress_failure_incomplete_dependee_tasks_of_superior_tasks(
    data_layer_mock: mock.MagicMock,
) -> None:
    assert True is False
