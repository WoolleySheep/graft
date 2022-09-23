import datetime

import pytest

from graft.task_attributes import AfterDueDatetimeError
from graft.task_network import (
    InferiorTaskStartDatetimeError,
    SuperiorTaskStartDatetimeError,
    TaskDoesNotExistError,
    TaskNetwork,
)


def test_single_task(task_network: TaskNetwork, datetime_example: datetime.datetime):
    # Given there is a single task in the network
    task_network.add_task("1")

    # When I set the start datetime
    task_network.set_start_datetime("1", datetime_example)

    # Then the new start datetime reflects the set value
    assert task_network._task_attributes_map["1"].start_datetime == datetime_example


def test_task_does_not_exist(
    task_network: TaskNetwork, datetime_example: datetime.datetime
):
    # Given that a task does not exist
    assert "1" not in task_network._task_attributes_map

    # When the start date of said task is set
    # Then an appropriate exception is raised
    with pytest.raises(TaskDoesNotExistError) as exc_info:
        task_network.set_start_datetime("1", datetime_example)
    assert exc_info.value.uid == "1"


def test_start_datetime_after_due_datetime(
    task_network: TaskNetwork,
    datetime_example: datetime.datetime,
    datetime_later_example: datetime.datetime,
):
    # Given the following task with the given due datetime
    task_network.add_task("1")
    task_network.set_due_datetime("1", datetime_example)

    # When a start datetime is set that is later than the start datetime
    # Then an appropriate exception is raised
    with pytest.raises(AfterDueDatetimeError) as exc_info:
        task_network.set_start_datetime("1", datetime_later_example)
    assert exc_info.value.due_datetime == datetime_example
    assert exc_info.value.start_datetime == datetime_later_example


def test_superior_task_already_has_start_datetime(
    task_network: TaskNetwork, datetime_example: datetime.datetime
):
    # Given a the following task hierarchies and start datetime
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    task_network.set_start_datetime("1", datetime_example)

    # When a due datetime is set for the inferior task
    # Then an appropriate exception is raised
    with pytest.raises(SuperiorTaskStartDatetimeError) as exc_info:
        task_network.set_start_datetime("3", datetime_example)
    assert exc_info.value.uid == "3"


def test_inferior_task_already_has_start_datetime(
    task_network: TaskNetwork, datetime_example: datetime.datetime
):
    # Given a the following task hierarchies and start datetime
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    task_network.set_start_datetime("3", datetime_example)

    # When a start datetime is set for the superior task
    # Then an appropriate exception is raised
    with pytest.raises(InferiorTaskStartDatetimeError) as exc_info:
        task_network.set_start_datetime("1", datetime_example)
    assert exc_info.value.uid == "1"


# TODO (mjw): Add extra tests like in test_set_due_datetime
