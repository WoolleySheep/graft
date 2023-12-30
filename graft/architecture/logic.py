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
    def initialise(self) -> None:
        """Initialise both the logic-layer and data-layer.

        This differs from instance initialisation - it refers to getting the
        logic layer ready when graft is used for the first time. Like `docker
        init` or `git init`.
        """

    @abc.abstractmethod
    def create_task(self) -> tasks.UID:
        """Create a new task and return its UID."""

    @abc.abstractmethod
    def delete_task(self, task: tasks.UID) -> None:
        """Delete the specified task."""

    @abc.abstractmethod
    def get_task_attributes_register_view(self) -> tasks.AttributesRegisterView:
        """Return a view of the task attributes register."""

    @abc.abstractmethod
    def create_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Create a new hierarchy between the specified tasks."""

    @abc.abstractmethod
    def delete_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Delete the specified hierarchy."""
