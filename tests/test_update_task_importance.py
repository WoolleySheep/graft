"""Unit tests for Standard.update_task_progress."""

import copy
import itertools
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


@pytest.mark.parametrize(
    ("task_importance", "supertask_importance"),
    list(itertools.combinations(iterable=tasks.Importance, r=2)),
)
@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_importance_failure_supertask_with_importance(
    data_layer_mock: mock.MagicMock,
    task_importance: tasks.Importance,
    supertask_importance: tasks.Importance,
) -> None:
    """Test that update_task_importance fails when a supertask has an importance."""
    task = tasks.UID(0)
    supertask = tasks.UID(1)
    system = domain.System.empty()

    system.add_task(task)
    system.add_task(supertask)
    system.add_task_hierarchy(supertask, task)
    system.set_task_importance(supertask, supertask_importance)

    data_layer_mock.load_system.return_value = system
    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.SupertaskHasImportanceError) as exc_info:
        logic_layer.update_task_importance(task=task, importance=task_importance)
    assert exc_info.value.task == task
    assert exc_info.value.supertasks_with_importance == [
        (supertask, supertask_importance)
    ]

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@pytest.mark.parametrize(
    ("task_importance", "superior_task_importance"),
    list(itertools.combinations(iterable=tasks.Importance, r=2)),
)
@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_importance_failure_superior_task_with_importance(
    data_layer_mock: mock.MagicMock,
    task_importance: tasks.Importance,
    superior_task_importance: tasks.Importance,
) -> None:
    """Test that update_task_importance fails when a superior-task has an importance."""
    task = tasks.UID(0)
    supertask = tasks.UID(1)
    superior_task = tasks.UID(2)
    system = domain.System.empty()

    system.add_task(task)
    system.add_task(supertask)
    system.add_task(superior_task)
    system.add_task_hierarchy(supertask, task)
    system.add_task_hierarchy(superior_task, supertask)
    system.set_task_importance(superior_task, superior_task_importance)

    data_layer_mock.load_system.return_value = system
    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.SuperiorTaskHasImportanceError) as exc_info:
        logic_layer.update_task_importance(task=task, importance=task_importance)
    assert exc_info.value.task == task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@pytest.mark.parametrize(
    ("task_importance", "subtask_importance"),
    list(itertools.combinations(iterable=tasks.Importance, r=2)),
)
@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_importance_failure_subtask_with_importance(
    data_layer_mock: mock.MagicMock,
    task_importance: tasks.Importance,
    subtask_importance: tasks.Importance,
) -> None:
    """Test that update_task_importance fails when a subtask has an importance."""
    task = tasks.UID(0)
    subtask = tasks.UID(1)
    system = domain.System.empty()

    system.add_task(task)
    system.add_task(subtask)
    system.add_task_hierarchy(task, subtask)
    system.set_task_importance(subtask, subtask_importance)

    data_layer_mock.load_system.return_value = system
    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.SubtaskHasImportanceError) as exc_info:
        logic_layer.update_task_importance(task=task, importance=task_importance)
    assert exc_info.value.task == task
    assert exc_info.value.subtasks_with_importance == [(subtask, subtask_importance)]

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@pytest.mark.parametrize(
    ("task_importance", "inferior_task_importance"),
    list(itertools.combinations(iterable=tasks.Importance, r=2)),
)
@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_task_importance_failure_inferior_task_with_importance(
    data_layer_mock: mock.MagicMock,
    task_importance: tasks.Importance,
    inferior_task_importance: tasks.Importance,
) -> None:
    """Test that update_task_importance fails when an inferior-task has an importance."""
    task = tasks.UID(0)
    subtask = tasks.UID(1)
    inferior_task = tasks.UID(2)
    system = domain.System.empty()

    system.add_task(task)
    system.add_task(subtask)
    system.add_task(inferior_task)
    system.add_task_hierarchy(task, subtask)
    system.add_task_hierarchy(subtask, inferior_task)
    system.set_task_importance(inferior_task, inferior_task_importance)

    data_layer_mock.load_system.return_value = system
    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.InferiorTaskHasImportanceError) as exc_info:
        logic_layer.update_task_importance(task=task, importance=task_importance)
    assert exc_info.value.task == task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False
