"""Logic-layer interface and associated exceptions."""

import abc

from graft.architecture import data
from graft.domain import tasks


class LogicLayer(abc.ABC):
    """Logic-layer interface."""

    def __init__(self, data_layer: data.DataLayer) -> None:
        """Initialize logic layer."""
        self._data_layer = data_layer

    @abc.abstractmethod
    def create_task(self) -> tasks.UID:
        """Create a new task and return its UID."""

    @abc.abstractmethod
    def delete_task(self, task: tasks.UID) -> None:
        """Delete the specified task."""

    @abc.abstractmethod
    def get_task_attributes_register_view(self) -> tasks.AttributesRegisterView:
        """Return the task attributes register."""

    @abc.abstractmethod
    def get_hierarchy_graph_view(self) -> tasks.HierarchyGraphView:
        """Return the hierarchy graph."""

    @abc.abstractmethod
    def get_dependency_graph_view(self) -> tasks.DependencyGraphView:
        """Return the dependency graph."""

    @abc.abstractmethod
    def create_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Create a new hierarchy between the specified tasks."""

    @abc.abstractmethod
    def delete_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Delete the specified hierarchy."""

    @abc.abstractmethod
    def create_dependency(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> None:
        """Create a new dependency between the specified tasks."""

    @abc.abstractmethod
    def delete_dependency(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> None:
        """Delete the specified dependency."""
