"""Data-layer interface and associated exceptions."""

import abc
from xml import dom

from graft import domain
from graft.domain import task


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
    def get_next_task_uid(self) -> task.UID:
        """Get the next task UID."""

    @abc.abstractmethod
    def increment_next_task_uid_counter(self) -> None:
        """Increment the task UID counter."""

    @abc.abstractmethod
    def save_system(self, system: domain.System) -> None:
        """Save the state of the system."""
        raise NotImplementedError

    @abc.abstractmethod
    def load_system(self) -> domain.System:
        """Load the state of the system."""
        raise NotImplementedError
