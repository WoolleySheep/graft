import copy
from unittest import mock

import pytest

from graft import domain
from graft.domain import tasks
from graft.standard import standard


@pytest.fixture()
def empty_system() -> domain.System:
    """Create an empty system."""
    return domain.System(
        task_system=tasks.System(
            attributes_register=tasks.AttributesRegister(),
            hierarchy_graph=tasks.HierarchyGraph(),
            dependency_graph=tasks.DependencyGraph(),
        )
    )



@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_task(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_task method works as expected."""
    task = tasks.UID(0)

    data_layer_mock.get_next_task_uid.return_value = task
    data_layer_mock.load_system.return_value = empty_system
    system_with_one_task = copy.deepcopy(empty_system)
    system_with_one_task.add_task(task)

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    assert logic_layer.create_task() == task

    data_layer_mock.get_next_task_uid.assert_called_once()
    data_layer_mock.load_system.assert_called_once()
    data_layer_mock.save_system.assert_called_once_with(system_with_one_task)


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_task_success(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the delete_task method works as expected."""
    task = tasks.UID(0)

    system_with_one_task = copy.deepcopy(empty_system)
    system_with_one_task.add_task(task)

    data_layer_mock.load_system.return_value = system_with_one_task

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.delete_task(task)

    data_layer_mock.load_system.assert_called_once()
    data_layer_mock.save_system.assert_called_once_with(empty_system)


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_task_failure_has_supertask(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the delete_task method fails when task has a super-task."""
    supertask = tasks.UID(0)
    subtask = tasks.UID(1)

    system_with_hierarchy = empty_system
    system_with_hierarchy.add_task(supertask)
    system_with_hierarchy.add_task(subtask)
    system_with_hierarchy.add_hierarchy(supertask=supertask, subtask=subtask)

    data_layer_mock.load_system.return_value = system_with_hierarchy

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HasSuperTasksError) as exc_info:
        logic_layer.delete_task(subtask)
    assert exc_info.value.task == subtask
    assert exc_info.value.supertasks == {supertask}

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_task_failure_has_subtask(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the delete_task method fails when task has a sub-task."""
    supertask = tasks.UID(0)
    subtask = tasks.UID(1)

    system_with_hierarchy = empty_system
    system_with_hierarchy.add_task(supertask)
    system_with_hierarchy.add_task(subtask)
    system_with_hierarchy.add_hierarchy(supertask=supertask, subtask=subtask)

    data_layer_mock.load_system.return_value = system_with_hierarchy

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HasSubTasksError) as exc_info:
        logic_layer.delete_task(supertask)
    assert exc_info.value.task == supertask
    assert exc_info.value.subtasks == {subtask}

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_task_failure_has_dependee_task(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the delete_task method fails when task has a dependee-task."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)

    system_with_dependency = empty_system
    system_with_dependency.add_task(dependee_task)
    system_with_dependency.add_task(dependent_task)
    system_with_dependency.add_dependency(
        dependee_task=dependee_task, dependent_task=dependent_task
    )

    data_layer_mock.load_system.return_value = system_with_dependency

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HasDependeeTasksError) as exc_info:
        logic_layer.delete_task(dependent_task)
    assert exc_info.value.task == dependent_task
    assert exc_info.value.dependee_tasks == {dependent_task}

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False
