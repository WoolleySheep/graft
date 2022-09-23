import datetime

import pytest
from graft.task_attributes import BeforeStartDatetimeError
from graft.task_network import (
    DueBeforeInferiorsUpstreamStartError,
    DueBeforeUpstreamStartError,
    InferiorStartDatetimeTooLate,
    InferiorTaskDueDatetimeError,
    SuperiorInferiorStartDatetimeTooLate,
    SuperiorStartDatetimeTooLate,
    SuperiorTaskDueDatetimeError,
    TaskDoesNotExistError,
    TaskNetwork,
)


def test_single_task(task_network: TaskNetwork, datetime_example: datetime.datetime):
    # Given there is a single task in the network
    task_network.add_task("1")

    # When I set the due datetime
    task_network.set_due_datetime("1", datetime_example)

    # Then the new due datetime reflects the set value
    assert task_network._task_attributes_map["1"].due_datetime == datetime_example


def test_task_does_not_exist(
    task_network: TaskNetwork, datetime_example: datetime.datetime
):
    # Given that a task does not exist
    assert "1" not in task_network._task_attributes_map

    # When the due date of said task is set
    # Then an appropriate exception is raised
    with pytest.raises(TaskDoesNotExistError) as exc_info:
        task_network.set_due_datetime("1", datetime_example)
    assert exc_info.value.uid == "1"


def test_due_datetime_before_start_datetime(
    task_network: TaskNetwork,
    datetime_example: datetime.datetime,
    datetime_earlier_example: datetime.datetime,
):
    # Given the following task with the given start datetime
    task_network.add_task("1")
    task_network.set_start_datetime("1", datetime_example)

    # When a due datetime is set that is earlier than the start datetime
    # Then an appropriate exception is raised
    with pytest.raises(BeforeStartDatetimeError) as exc_info:
        task_network.set_due_datetime("1", datetime_earlier_example)
    assert exc_info.value.due_datetime == datetime_earlier_example
    assert exc_info.value.start_datetime == datetime_example


def test_superior_task_already_has_due_datetime(
    task_network: TaskNetwork, datetime_example: datetime.datetime
):
    # Given a the following task hierarchies and due datetime
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    task_network.set_due_datetime("1", datetime_example)

    # When a due datetime is set for the inferior task
    # Then an appropriate exception is raised
    with pytest.raises(SuperiorTaskDueDatetimeError) as exc_info:
        task_network.set_due_datetime("3", datetime_example)
    assert exc_info.value.uid == "3"


def test_inferior_task_already_has_due_datetime(
    task_network: TaskNetwork, datetime_example: datetime.datetime
):
    # Given a the following task hierarchies and due datetime
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    task_network.set_due_datetime("3", datetime_example)

    # When a due datetime is set for the superior task
    # Then an appropriate exception is raised
    with pytest.raises(InferiorTaskDueDatetimeError) as exc_info:
        task_network.set_due_datetime("1", datetime_example)
    assert exc_info.value.uid == "1"


def test_due_datetime_earlier_than_any_superiors_start_datetime(
    task_network: TaskNetwork,
    datetime_example: datetime.datetime,
    datetime_earlier_example: datetime.datetime,
) -> None:
    # Given the following task hierarchy and start datetime
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    task_network.set_start_datetime(uid="1", start_datetime=datetime_example)

    # When a due datetime is set which is earlier than the start datetime of any superior tasks
    # Then an appropriate exception is raised
    with pytest.raises(SuperiorStartDatetimeTooLate) as exc_info:
        task_network.set_due_datetime(uid="3", due_datetime=datetime_earlier_example)
    assert exc_info.value.uid == "3"


def test_due_datetime_earlier_than_any_inferiors_start_datetime(
    task_network: TaskNetwork,
    datetime_example: datetime.datetime,
    datetime_earlier_example: datetime.datetime,
) -> None:
    # Given the following task hierarchy and start datetime
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    task_network.set_start_datetime(uid="3", start_datetime=datetime_example)

    # When a due datetime is set which is earlier than the start datetime of any inferior tasks
    # Then an appropriate exception is raised
    with pytest.raises(InferiorStartDatetimeTooLate) as exc_info:
        task_network.set_due_datetime(uid="1", due_datetime=datetime_earlier_example)
    assert exc_info.value.uid == "1"


def test_due_datetime_earlier_than_any_inferior_tasks_superior_start_datetime(
    task_network: TaskNetwork,
    datetime_example: datetime.datetime,
    datetime_earlier_example: datetime.datetime,
) -> None:
    # Given the following task hierarchy and start datetime
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_task("4")
    task_network.add_task("5")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    task_network.add_hierarchy("4", "5")
    task_network.add_hierarchy("5", "3")
    task_network.set_start_datetime(uid="4", start_datetime=datetime_example)

    # When a due datetime is set which is earlier than the start datetime of superior
    # tasks of any inferior tasks
    # Then an appropriate exception is raised
    with pytest.raises(SuperiorInferiorStartDatetimeTooLate) as exc_info:
        task_network.set_due_datetime(uid="1", due_datetime=datetime_earlier_example)
    assert exc_info.value.uid == "1"


def test_due_datetime_earlier_than_any_upstream_start_datetime(
    task_network: TaskNetwork,
    datetime_example: datetime.datetime,
    datetime_earlier_example: datetime.datetime,
):
    # Given the following task network and start datetime
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_dependency("1", "2")
    task_network.add_hierarchy("2", "3")
    task_network.set_start_datetime(uid="1", start_datetime=datetime_example)

    # When a due datetime is set that is earlier than a start datetime of an upstream task
    # Then the appropriate examption is raised
    with pytest.raises(DueBeforeUpstreamStartError) as exc_info:
        task_network.set_due_datetime("3", due_datetime=datetime_earlier_example)
    assert exc_info.value.uid == "3"


def test_due_datetime_earlier_than_inferior_tasks_upstream_start_datetime(
    task_network: TaskNetwork,
    datetime_example: datetime.datetime,
    datetime_earlier_example: datetime.datetime,
):
    # Raise an exception if the set due datetime is earlier than the start
    # datetime of any upstream tasks of any of the task's inferior tasks

    # Given the following task network and start datetime
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_task("4")
    task_network.add_hierarchy("1", "2")
    task_network.add_dependency("1", "3")
    task_network.add_hierarchy("4", "3")
    task_network.set_start_datetime(uid="2", start_datetime=datetime_example)

    # When a due datetime is set that is earlier than the start datetime of a
    # task upstream of an inferior task
    # Then the appropriate exception is raised
    with pytest.raises(DueBeforeInferiorsUpstreamStartError) as exc_info:
        task_network.set_due_datetime(uid="4", due_datetime=datetime_earlier_example)
    assert exc_info.value.uid == "4"
