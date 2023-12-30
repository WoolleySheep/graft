import copy
from unittest import mock

import pytest

from graft import domain, graphs
from graft.domain import tasks
from graft.standard import standard


@pytest.fixture
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
def test_initialise(data_layer_mock: mock.MagicMock) -> None:
    """Test the initialise method works as expected."""
    data_layer_mock.initialise.return_value = None

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.initialise()

    data_layer_mock.initialise.assert_called_once()


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_task(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_task method works as expected."""
    data_layer_mock.get_next_task_uid.return_value = tasks.UID(0)
    data_layer_mock.load_system.return_value = empty_system
    system_with_one_task = copy.deepcopy(empty_system)
    system_with_one_task.add_task(tasks.UID(0))

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    assert logic_layer.create_task() == tasks.UID(0)

    data_layer_mock.get_next_task_uid.assert_called_once()
    data_layer_mock.load_system.assert_called_once()
    data_layer_mock.save_system.assert_called_once_with(system_with_one_task)

@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_task_success(
    data_layer_mock: mock.MagicMock, empty_system: domain.System) -> None:
    """Test the delete_task method works as expected."""
    system_with_one_task = copy.deepcopy(empty_system)
    system_with_one_task.add_task(tasks.UID(0))

    data_layer_mock.load_system.return_value = system_with_one_task

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.delete_task(tasks.UID(0))

    data_layer_mock.load_system.assert_called_once()
    data_layer_mock.save_system.assert_called_once_with(empty_system)

@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_delete_task_failure_has_supertask(
    data_layer_mock: mock.MagicMock, empty_system: domain.System) -> None:
    """Test the delete_task method fails when task has a supertask."""
    system_with_hierarchy = empty_system
    system_with_hierarchy.add_task(tasks.UID(0))
    system_with_hierarchy.add_task(tasks.UID(1))
    system_with_hierarchy.add_hierarchy(supertask=tasks.UID(1), subtask=tasks.UID(0))

    data_layer_mock.load_system.return_value = system_with_hierarchy

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.HasSuperTasksError) as exc_info:
        logic_layer.delete_task(tasks.UID(0))
    assert exc_info.value.task == tasks.UID(0)
    assert exc_info.value.supertasks == {tasks.UID(1)}

    data_layer_mock.load_system.assert_called_once()
    assert not data_layer_mock.save_system.called
