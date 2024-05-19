"""Unit tests for Standard.update_task_progress."""

import copy
from unittest import mock

import pytest

from graft import domain, standard
from graft.domain import tasks


@pytest.mark.parametrize(
    "old_importance",
    [tasks.Importance.LOW, tasks.Importance.MEDIUM, tasks.Importance.HIGH, None],
)
@pytest.mark.parametrize(
    "new_importance",
    [tasks.Importance.LOW, tasks.Importance.MEDIUM, tasks.Importance.HIGH, None],
)
@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_importance_success_one_task(
    data_layer_mock: mock.MagicMock,
    new_importance: tasks.Importance | None,
    old_importance: tasks.Importance | None,
) -> None:
    """Test that update_task_importance works for a single task."""
    task = tasks.UID(0)
    system = domain.System.empty()

    system.add_task(task)
    system.set_task_importance(task, old_importance)

    system_with_new_importance = copy.deepcopy(system)
    system_with_new_importance.set_task_importance(task, new_importance)

    data_layer_mock.load_system.return_value = system
    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.update_task_importance(task=task, importance=new_importance)

    data_layer_mock.load_system.assert_called_once_with()
    data_layer_mock.save_system.assert_called_once_with(system_with_new_importance)


def test_update_task_importance_failure_supertask_with_importance() -> None:
    raise NotImplementedError


def test_update_task_importance_failure_superior_task_with_importance() -> None:
    raise NotImplementedError


def test_update_task_importance_failure_subtask_with_importance() -> None:
    raise NotImplementedError


def test_update_task_importance_failure_inferior_task_with_importance() -> None:
    raise NotImplementedError
