import datetime

import pytest
from graft.task_attributes import AfterDueDatetimeError, BeforeStartDatetimeError
from graft.task_network import TaskDoesNotExistError, TaskNetwork


def test_single_task(task_network: TaskNetwork):
    # Given there is a single task in the network
    task_network.add_task("1")

    # When I set the start datetime
    current_datetime = datetime.datetime.now()
    task_network.set_start_datetime("1", current_datetime)

    # Then the new start datetime reflects the set value
    assert task_network._task_attributes_map["1"].start_datetime == current_datetime


def test_task_does_not_exist(task_network: TaskNetwork):
    # Given that a task does not exist
    assert "1" not in task_network._task_attributes_map

    # When the start date of said task is set
    # Then an appropriate exception is raised
    current_datetime = datetime.datetime.now()
    with pytest.raises(TaskDoesNotExistError) as exc_info:
        task_network.set_start_datetime("1", current_datetime)
    assert exc_info.value.uid == "1"


def test_start_datetime_after_due_datetime(task_network: TaskNetwork):
    # Given the following task with the given due datetime
    task_network.add_task("1")
    due_datetime = datetime.datetime.now()
    task_network.set_due_datetime("1", due_datetime)

    # When a start datetime is set that is later than the start datetime
    # Then an appropriate exception is raised
    later_start_datetime = due_datetime + datetime.timedelta(days=1)
    with pytest.raises(AfterDueDatetimeError) as exc_info:
        task_network.set_start_datetime("1", later_start_datetime)
    assert exc_info.value.due_datetime == due_datetime
    assert exc_info.value.start_datetime == later_start_datetime
