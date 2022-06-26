import pytest

from graft.task_network import (
    HasDependeeTasksError,
    HasDependentTasksError,
    HasSubTasksError,
    HasSuperTasksError,
    TaskDoesNotExistError,
)


def test_remove_task_when_exists_and_no_relationships(task_network):
    # Given a task  exists in a network
    # And has no relationship to any other tasks
    task_network.add_task("1")
    assert "1" in task_network._task_attributes_map
    assert "1" in task_network._task_hierarchy
    assert "1" in task_network._task_dependencies

    # When the task is removed from the network
    task_network.remove_task("1")

    # Then it is removed from each of the components
    assert "1" not in task_network._task_attributes_map
    assert "1" not in task_network._task_hierarchy
    assert "1" not in task_network._task_dependencies


def test_remove_task_when_does_not_exist(task_network):
    # Given a task is not present in the network
    assert "1" not in task_network._task_attributes_map
    assert "1" not in task_network._task_hierarchy
    assert "1" not in task_network._task_dependencies

    # When the task is removed from the network
    # Then the appropriate is raised
    with pytest.raises(TaskDoesNotExistError) as exc_info:
        task_network.remove_task("1")
    assert exc_info.value.uid == "1"


def test_remove_task_when_has_supertask(task_network):
    # Given that a task is present in the network
    # And has a supertask
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_hierarchy("1", "2")
    assert task_network._task_hierarchy.has_edge("1", "2")

    # When the task is removed from the network
    # Then the appropriate is raised
    with pytest.raises(HasSuperTasksError) as exc_info:
        task_network.remove_task("2")
    assert exc_info.value.uid == "2"
    assert exc_info.value.supertasks == {"1"}


def test_remove_task_when_has_subtask(task_network):
    # Given that a task is present in the network
    # And has a subtask
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_hierarchy("1", "2")
    assert task_network._task_hierarchy.has_edge("1", "2")

    # When the task is removed from the network
    # Then the appropriate exception is raised
    with pytest.raises(HasSubTasksError) as exc_info:
        task_network.remove_task("1")
    assert exc_info.value.uid == "1"
    assert exc_info.value.subtasks == {"2"}


def test_remove_task_when_has_dependee_task(task_network):
    # Given that a task is present in the network
    # And has a dependent task
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_dependency("1", "2")
    assert task_network._task_dependencies.has_edge("1", "2")

    # When the task is removed from the network
    # Then the appropriate is raised
    with pytest.raises(HasDependeeTasksError) as exc_info:
        task_network.remove_task("2")
    assert exc_info.value.uid == "2"
    assert exc_info.value.dependee_tasks == {"1"}


def test_remove_task_when_has_dependent_task(task_network):
    # Given that a task is present in the network
    # And has a dependent task
    task_network.add_task("1")
    task_network.add_task("2")
    task_network.add_dependency("1", "2")
    assert task_network._task_dependencies.has_edge("1", "2")

    # When the task is removed from the network
    # Then the appropriate is raised
    with pytest.raises(HasDependentTasksError) as exc_info:
        task_network.remove_task("1")
    assert exc_info.value.uid == "1"
    assert exc_info.value.dependent_tasks == {"2"}
