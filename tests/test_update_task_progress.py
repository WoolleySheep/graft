"""Unit tests for logic.update_task_description."""

import copy
from unittest import mock

import pytest

from graft import domain
from graft.domain import tasks
from graft.layers import logic


@pytest.mark.parametrize(
    "old_progress",
    [tasks.Progress.NOT_STARTED, tasks.Progress.IN_PROGRESS, tasks.Progress.COMPLETED],
)
@pytest.mark.parametrize(
    "new_progress",
    [tasks.Progress.NOT_STARTED, tasks.Progress.IN_PROGRESS, tasks.Progress.COMPLETED],
)
@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_concrete_task_progress_success_one_task(
    data_layer_mock: mock.MagicMock,
    new_progress: tasks.Progress,
    old_progress: tasks.Progress,
) -> None:
    """Test that update_concrete_task_progress works for a single task."""
    task = tasks.UID(0)
    system = domain.System.empty()

    system.add_task(task)
    system.set_task_progress(task=task, progress=old_progress)

    system_with_new_progress = copy.deepcopy(system)
    system_with_new_progress.set_task_progress(task=task, progress=new_progress)

    data_layer_mock.load_system.return_value = system
    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.update_concrete_task_progress(task=task, progress=new_progress)

    data_layer_mock.load_system.assert_called_once_with()
    data_layer_mock.save_system.assert_called_once_with(system_with_new_progress)


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_concrete_task_progress_failure_task_does_not_exist(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test the update_concrete_task_progress method fails when the task does not exist."""
    task = tasks.UID(0)
    data_layer_mock.load_system.return_value = domain.System.empty()
    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.TaskDoesNotExistError) as e:
        logic_layer.update_concrete_task_progress(
            task=task, progress=tasks.Progress.COMPLETED
        )
    assert e.value.task == task

    data_layer_mock.load_system.assert_called_once_with()
    data_layer_mock.save_system.assert_not_called()


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_concrete_task_progress_failure_task_is_not_concrete(
    data_layer_mock: mock.MagicMock,
) -> None:
    """Test that update_concrete_task_progress fails for a non-concrete task."""
    supertask = tasks.UID(0)
    subtask = tasks.UID(1)
    system = domain.System.empty()

    system.add_task(supertask)
    system.add_task(subtask)
    system.add_task_hierarchy(supertask, subtask)

    data_layer_mock.load_system.return_value = system
    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.NotConcreteTaskError) as e:
        logic_layer.update_concrete_task_progress(
            task=supertask, progress=tasks.Progress.IN_PROGRESS
        )
    assert e.value.task == supertask

    data_layer_mock.load_system.assert_called_once_with()
    data_layer_mock.save_system.assert_not_called()


@pytest.mark.parametrize(
    "incomplete_progress",
    [tasks.Progress.NOT_STARTED, tasks.Progress.IN_PROGRESS],
)
@pytest.mark.parametrize(
    "started_progress",
    [tasks.Progress.IN_PROGRESS, tasks.Progress.COMPLETED],
)
@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_concrete_task_progress_failure_started_dependent_tasks(
    data_layer_mock: mock.MagicMock,
    started_progress: tasks.Progress,
    incomplete_progress: tasks.Progress,
) -> None:
    """Test that update_concrete_task_progress fails if the task is complete, has any started dependent tasks, and attempt to change progress to incomplete."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)
    system = domain.System.empty()

    system.add_task(dependee_task)
    system.add_task(dependent_task)
    system.add_task_dependency(dependee_task, dependent_task)

    system.set_task_progress(dependee_task, tasks.Progress.COMPLETED)
    system.set_task_progress(dependent_task, started_progress)

    data_layer_mock.load_system.return_value = system
    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.StartedDependentTasksError) as e:
        logic_layer.update_concrete_task_progress(
            task=dependee_task, progress=incomplete_progress
        )
    assert e.value.task == dependee_task
    assert e.value.dependee_tasks_with_progress == [(dependent_task, started_progress)]

    data_layer_mock.load_system.assert_called_once_with()
    data_layer_mock.save_system.assert_not_called()


@pytest.mark.parametrize(
    "incomplete_progress",
    [tasks.Progress.NOT_STARTED, tasks.Progress.IN_PROGRESS],
)
@pytest.mark.parametrize(
    "started_progress",
    [tasks.Progress.IN_PROGRESS, tasks.Progress.COMPLETED],
)
@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_concrete_task_progress_failure_started_dependent_tasks_of_superior_tasks(
    data_layer_mock: mock.MagicMock,
    started_progress: tasks.Progress,
    incomplete_progress: tasks.Progress,
) -> None:
    """Test that update_concrete_task_progress fails if the task is complete, has any started dependent tasks of super-tasks, and attempt to change progress to incomplete."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    system = domain.System.empty()

    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)

    system.add_task_hierarchy(task0, task1)
    system.add_task_dependency(task0, task2)
    system.set_task_progress(task1, tasks.Progress.COMPLETED)
    system.set_task_progress(task2, started_progress)

    data_layer_mock.load_system.return_value = system
    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.StartedDependentTasksOfSuperiorTasksError) as e:
        logic_layer.update_concrete_task_progress(
            task=task1, progress=incomplete_progress
        )
    assert e.value.task == task1

    data_layer_mock.load_system.assert_called_once_with()
    data_layer_mock.save_system.assert_not_called()


@pytest.mark.parametrize(
    "incomplete_progress",
    [tasks.Progress.NOT_STARTED, tasks.Progress.IN_PROGRESS],
)
@pytest.mark.parametrize(
    "started_progress",
    [tasks.Progress.IN_PROGRESS, tasks.Progress.COMPLETED],
)
@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_concrete_task_progress_failure_incomplete_dependee_tasks(
    data_layer_mock: mock.MagicMock,
    started_progress: tasks.Progress,
    incomplete_progress: tasks.Progress,
) -> None:
    """Test that update_concrete_task_progress fails if the task is not started, has any incomplete dependee tasks, and attempt to change progress to started."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)
    system = domain.System.empty()

    system.add_task(dependee_task)
    system.add_task(dependent_task)
    system.add_task_dependency(dependee_task, dependent_task)

    system.set_task_progress(dependee_task, incomplete_progress)

    data_layer_mock.load_system.return_value = system
    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.IncompleteDependeeTasksError) as e:
        logic_layer.update_concrete_task_progress(
            task=dependent_task, progress=started_progress
        )
    assert e.value.task == dependent_task
    assert e.value.incomplete_dependee_tasks_with_progress == [
        (dependee_task, incomplete_progress)
    ]

    data_layer_mock.load_system.assert_called_once_with()
    data_layer_mock.save_system.assert_not_called()


@pytest.mark.parametrize(
    "incomplete_progress",
    [tasks.Progress.NOT_STARTED, tasks.Progress.IN_PROGRESS],
)
@pytest.mark.parametrize(
    "started_progress",
    [tasks.Progress.IN_PROGRESS, tasks.Progress.COMPLETED],
)
@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_update_concrete_task_progress_failure_incomplete_dependee_tasks_of_superior_tasks(
    data_layer_mock: mock.MagicMock,
    started_progress: tasks.Progress,
    incomplete_progress: tasks.Progress,
) -> None:
    """Test that update_concrete_task_progress fails if the task is not started, has any incomplete dependee tasks of super-tasks, and attempt to change progress to started."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    system = domain.System.empty()

    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)

    system.add_task_hierarchy(task0, task1)
    system.add_task_dependency(task2, task0)
    system.set_task_progress(task2, incomplete_progress)

    data_layer_mock.load_system.return_value = system
    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.IncompleteDependeeTasksOfSuperiorTasksError) as e:
        logic_layer.update_concrete_task_progress(task=task1, progress=started_progress)
    assert e.value.task == task1

    data_layer_mock.load_system.assert_called_once_with()
    data_layer_mock.save_system.assert_not_called()
