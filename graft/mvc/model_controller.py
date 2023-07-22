"""Define interface between the Model & Controller."""

import enum
from typing import Any, Self


class Topic(enum.Enum):
    """Request topics between the model and the controller."""

    GET_TASK_GRAPHS = enum.auto()


class Status(enum.Enum):
    """Request statuses."""

    SUCCESS = enum.auto()
    FAILURE = enum.auto()


class Request:
    """Request sent from the controller to the model."""

    @classmethod
    def get_task_graphs(cls) -> Self:
        """'Get task graphs' request."""
        return cls(topic=Topic.GET_TASK_GRAPHS, data=None)

    def __init__(self, topic: Topic, data: Any = None) -> None:
        """Initialize request."""
        self.topic = topic
        self.data = data


class Response:
    """Response sent from the model to the controller."""

    def __init__(self, topic: Topic, status: Status, data: Any = None) -> None:
        """Initialize response."""
        self.topic = topic
        self.status = status
        self.data = data
