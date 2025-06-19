"""Unit tests for `System.create_task`."""

from unittest import mock

from graft import domain
from graft.domain import tasks
from graft.layers import logic


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_task(data_layer_mock: mock.MagicMock) -> None:
    """Test the create_task method works as expected."""
    task = tasks.UID(0)
    empty_system = domain.System.empty()

    data_layer_mock.load_next_unused_task.return_value = task
    data_layer_mock.load_system.return_value = empty_system
    system_with_one_task = domain.System.empty()
    system_with_one_task.add_task(task)

    logic_layer = logic.StandardLogicLayer(data_layer=data_layer_mock)

    assert logic_layer.create_task() == task

    data_layer_mock.load_next_unused_task.assert_called_once()
    data_layer_mock.load_system.assert_called_once()
    data_layer_mock.save_system_and_indicate_task_used.assert_called_once_with(
        system_with_one_task, task
    )
