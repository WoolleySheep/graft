import copy
from unittest import mock

from graft import domain
from graft.domain import tasks
from graft.standard import standard


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
