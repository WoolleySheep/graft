import datetime

import pytest
from graft.task_attributes import BeforeStartDatetimeError
from graft.task_network import (
    InferiorTaskDueDatetimeError,
    SuperiorTaskDueDatetimeError,
    TaskDoesNotExistError,
    TaskNetwork,
)


def test_single_task(task_network: TaskNetwork):
    # Given there is a single task in the network
    task_network.add_task("1")

    # When I set the due datetime
    current_datetime = datetime.datetime.now()
    task_network.set_due_datetime("1", current_datetime)

    # Then the new due datetime reflects the set value
    assert task_network._task_attributes_map["1"].due_datetime == current_datetime


def test_task_does_not_exist(task_network: TaskNetwork):
    # Given that a task does not exist
    assert "1" not in task_network._task_attributes_map

    # When the due date of said task is set
    # Then an appropriate exception is raised
    current_datetime = datetime.datetime.now()
    with pytest.raises(TaskDoesNotExistError) as exc_info:
        task_network.set_due_datetime("1", current_datetime)
    assert exc_info.value.uid == "1"


def test_due_datetime_before_start_datetime(task_network: TaskNetwork):
    # Given the following task with the given start datetime
    task_network.add_task("1")
    start_datetime = datetime.datetime.now()
    task_network.set_start_datetime("1", start_datetime)

    # When a due datetime is set that is earlier than the start datetime
    # Then an appropriate exception is raised
    earlier_due_datetime = start_datetime - datetime.timedelta(days=1)
    with pytest.raises(BeforeStartDatetimeError) as exc_info:
        task_network.set_due_datetime("1", earlier_due_datetime)
    assert exc_info.value.due_datetime == earlier_due_datetime
    assert exc_info.value.start_datetime == start_datetime


def test_superior_task_already_has_due_datetime(task_network: TaskNetwork):
    # Given a the following task hierarchies and due datetime
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    task_network.set_due_datetime("1", datetime.datetime.now())

    # When a due datetime is set for the inferior task
    # Then an appropriate exception is raised
    with pytest.raises(SuperiorTaskDueDatetimeError) as exc_info:
        task_network.set_due_datetime("3", datetime.datetime.now())
    assert exc_info.value.uid == "3"


def test_inferior_task_already_has_due_datetime(task_network: TaskNetwork):
    # Given a the following task hierarchies and due datetime
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    task_network.set_due_datetime("3", datetime.datetime.now())

    # When a due datetime is set for the superior task
    # Then an appropriate exception is raised
    with pytest.raises(InferiorTaskDueDatetimeError) as exc_info:
        task_network.set_due_datetime("1", datetime.datetime.now())
    assert exc_info.value.uid == "1"
