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
    data_layer_mock: mock.MagicMock, empty_system: domain.System) -> None:
    """Test the delete_dependency method fails when the dependee task does not exist."""
    raise NotImplementedError
