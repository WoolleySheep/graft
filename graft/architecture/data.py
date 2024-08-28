"""Data-layer interface and associated exceptions."""

import abc

from graft import domain
from graft.domain import tasks


class DataLayer(abc.ABC):
    """Data-layer interface."""

    @abc.abstractmethod
    def get_next_unused_task(self) -> tasks.UID:
        """Get the next unused task UID.

        "Unused" means that the UID has never been used in the system before,
        regardless of whether the task had subsequently been deleted.

        Loading an unused task UID will not add it to the system, and will
        return the same value if called multiple times. The returned value will
        only change once a system containing the task uid is saved.
        """

    @abc.abstractmethod
    def load_system(self) -> domain.System:
        """Load the state of the system."""

    @abc.abstractmethod
    def erase(self) -> None:
        """Erase all data."""

    @abc.abstractmethod
    def save_system(self, system: domain.System) -> None:
        """Save the state of the system."""

    @abc.abstractmethod
    def save_system_and_indicate_task_used(
        self, system: domain.System, used_task: tasks.UID
    ) -> None:
        """Save the state of the system and indicate that a new task has been added."""
