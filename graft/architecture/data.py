"""Data-layer interface and associated exceptions."""

import abc

from graft import domain
from graft.domain import tasks


class DataLayer(abc.ABC):
    """Data-layer interface."""

    @abc.abstractmethod
    def initialise(self) -> None:
        """Initialise the data-layer.

        This differs from instance initialisation - it refers to getting the
        logic layer ready when graft is used for the first time. Like `docker
        init` or `git init`.
        """

    @abc.abstractmethod
    def get_next_task_uid(self) -> tasks.UID:
        """Get the next task UID."""

    @abc.abstractmethod
    def increment_next_task_uid_counter(self) -> None:
        """Increment the task UID counter."""

    @abc.abstractmethod
    def save_system(self, system: domain.System) -> None:
        """Save the state of the system."""

    @abc.abstractmethod
    def load_system(self) -> domain.System:
        """Load the state of the system."""

    @abc.abstractmethod
    def load_task_attributes_register(self) -> tasks.AttributesRegister:
        """Return the task attributes register."""

    @abc.abstractmethod
    def load_task_hierarchy_graph(self) -> tasks.HierarchyGraph:
        """Return the task hierarchy graph."""

    @abc.abstractmethod
    def load_task_dependency_graph(self) -> tasks.DependencyGraph:
        """Return the task dependency graph."""
