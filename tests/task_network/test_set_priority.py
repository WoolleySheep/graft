import collections

import pytest
from graft.priority import Priority
from graft.task_network import (
    InferiorTaskPrioritiesError,
    SuperiorTaskPrioritiesError,
    TaskDoesNotExistError,
    TaskNetwork,
)


def test_add_priority(task_network: TaskNetwork):
    # Given a single task with no priority set
    task_network.add_task("1")
    assert task_network._task_attributes_map["1"].priority is None

    # When a priority is set
    task_network.set_priority("1", Priority.MEDIUM)

    # Then the priority of the task reflects the set value
    assert task_network._task_attributes_map["1"].priority is Priority.MEDIUM


def test_non_existent_task(task_network: TaskNetwork):
    # Given that a task does not exist
    assert "1" not in task_network._task_attributes_map

    # When a priority is set for said task
    # Then an appropriate exception is raised
    with pytest.raises(TaskDoesNotExistError) as exc_info:
        task_network.set_priority("1", Priority.MEDIUM)
    assert exc_info.value.uid == "1"


def test_supertask_already_has_priority(task_network: TaskNetwork):
    # Given a the following task hierarchy and priority
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_hierarchy("1", "2")
    task_network.set_priority("1", Priority.MEDIUM)

    # When a priority is set for the subtask
    # Then an appropriate exception is raised
    with pytest.raises(SuperiorTaskPrioritiesError) as exc_info:
        task_network.set_priority("2", Priority.MEDIUM)
    assert exc_info.value.uid == "2"
    assert exc_info.value.superior_tasks_with_priorities == ["1"]


def test_superior_task_already_has_priority(task_network: TaskNetwork):
    # Given a the following task hierarchies and priority
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    task_network.set_priority("1", Priority.MEDIUM)

    # When a priority is set for the inferior task
    # Then an appropriate exception is raised
    with pytest.raises(SuperiorTaskPrioritiesError) as exc_info:
        task_network.set_priority("3", Priority.MEDIUM)
    assert exc_info.value.uid == "3"
    assert exc_info.value.superior_tasks_with_priorities == ["1"]


def test_multiple_priorities(task_network: TaskNetwork):
    # Given a the following task hierarchies and priorities
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "3")
    task_network.add_hierarchy("2", "3")
    task_network.set_priority("1", Priority.MEDIUM)
    task_network.set_priority("2", Priority.HIGH)

    # When a priority is set for the inferior task
    # Then an appropriate exception is raised
    with pytest.raises(SuperiorTaskPrioritiesError) as exc_info:
        task_network.set_priority("3", Priority.MEDIUM)
    assert exc_info.value.uid == "3"
    expected_counter = collections.Counter(["1", "2"])
    assert (
        collections.Counter(exc_info.value.superior_tasks_with_priorities)
        == expected_counter
    )


def test_inferior_task_already_has_priority(task_network: TaskNetwork):
    # Given a the following task hierarchies and priority
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_task("3")
    task_network.add_hierarchy("1", "2")
    task_network.add_hierarchy("2", "3")
    task_network.set_priority("3", Priority.MEDIUM)

    # When a priority is set for the superior task
    # Then an appropriate exception is raised
    with pytest.raises(InferiorTaskPrioritiesError) as exc_info:
        task_network.set_priority("1", Priority.MEDIUM)
    assert exc_info.value.uid == "1"
