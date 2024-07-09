"""Logic-layer interface and associated exceptions."""

import abc
from collections.abc import Generator

from graft.architecture import data
from graft.domain import tasks


class LogicLayer(abc.ABC):
    """Logic-layer interface."""

    def __init__(self, data_layer: data.DataLayer) -> None:
        """Initialize logic layer."""
        self._data_layer = data_layer

    @abc.abstractmethod
    def erase(self) -> None:
        """Erase all data."""

    @abc.abstractmethod
    def create_task(
        self,
        name: tasks.Name | None = None,
        description: tasks.Description | None = None,
    ) -> tasks.UID:
        """Create a new task and return its UID."""

    @abc.abstractmethod
    def get_next_task_id(self) -> tasks.UID:
        """Return the next task ID."""

    @abc.abstractmethod
    def delete_task(self, task: tasks.UID) -> None:
        """Delete the specified task."""

    @abc.abstractmethod
    def update_task_name(self, task: tasks.UID, name: tasks.Name) -> None:
        """Update the specified task's name."""

    @abc.abstractmethod
    def update_task_description(
        self, task: tasks.UID, description: tasks.Description
    ) -> None:
        """Update the specified task's description."""

    @abc.abstractmethod
    def update_task_progress(self, task: tasks.UID, progress: tasks.Progress) -> None:
        """Update the specified task's progress."""

    @abc.abstractmethod
    def update_task_importance(
        self, task: tasks.UID, importance: tasks.Importance | None = None
    ) -> None:
        """Update the specified task's importance."""

    @abc.abstractmethod
    def get_task_attributes_register_view(self) -> tasks.AttributesRegisterView:
        """Return the task attributes register."""

    @abc.abstractmethod
    def get_task_hierarchy_graph_view(self) -> tasks.HierarchyGraphView:
        """Return the hierarchy graph."""

    @abc.abstractmethod
    def get_task_dependency_graph_view(self) -> tasks.DependencyGraphView:
        """Return the dependency graph."""

    @abc.abstractmethod
    def get_task_system_view(self) -> tasks.SystemView:
        """Return the task system."""

    @abc.abstractmethod
    def create_task_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Create a new hierarchy between the specified tasks."""

    @abc.abstractmethod
    def delete_task_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Delete the specified hierarchy."""

    @abc.abstractmethod
    def create_task_dependency(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> None:
        """Create a new dependency between the specified tasks."""

    @abc.abstractmethod
    def delete_task_dependency(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> None:
        """Delete the specified dependency."""

    @abc.abstractmethod
    def get_active_concrete_tasks_in_order_of_descending_priority(
        self,
    ) -> Generator[tuple[tasks.UID, tasks.Importance | None], None, None]:
        """Return the active concrete tasks in order of descending priority.

        Tasks are paired with the maximum importance of downstream tasks.
        """
