"""Logic-layer interface and associated exceptions."""

import abc

from graft.architecture import data
from graft.domain import task


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
    def create_task(self) -> task.UID:
        """Create a new task and return its ID."""
