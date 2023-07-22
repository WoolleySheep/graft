"""Define interface between the View & Controller."""

import enum
from typing import Any, Self


class Topic(enum.Enum):
    """Request topics between the view and the controller."""

    # Not yet created
    INITIALISE = enum.auto()
    ERASE = enum.auto()

    CREATE_TASK = enum.auto()
    DELETE_TASK = enum.auto()
    UPDATE_TASK_NAME = enum.auto()
    UPDATE_TASK_DESCRIPTION = enum.auto()
    UPDATE_TASK_IMPORTANCE = enum.auto()
    UPDATE_TASK_PROGRESS = enum.auto()
    READ_TASK_DETAILS = enum.auto()

    CREATE_DEPENDENCY = enum.auto()
    DELETE_DEPENDENCY = enum.auto()

    CREATE_HIERARCHY = enum.auto()
    DELETE_HIERARCHY = enum.auto()

    CREATE_EVENT = enum.auto()
    DELETE_EVENT = enum.auto()
    UPDATE_EVENT_NAME = enum.auto()
    UPDATE_EVENT_DESCRIPTION = enum.auto()
    UPDATE_EVENT_DATETIME = enum.auto()
    READ_EVENT_DETAILS = enum.auto()

    CREATE_DUE_BY = enum.auto()
    DELETE_DUE_BY = enum.auto()


class Status(enum.Enum):
    """Request statuses."""

    SUCCESS = enum.auto()
    FAILURE = enum.auto()


class Request:
    """Request sent from the view to the controller."""

    @classmethod
    def create_task(cls) -> Self:
        """'Create task' request."""
        return cls(topic=Topic.CREATE_TASK, data=None)

    def __init__(self, topic: Topic, data: Any = None) -> None:
        """Initialize request."""
        self.topic = topic
        self.data = data


class Response:
    """Response sent from the controller to the view."""

    def __init__(self, topic: Topic, status: Status, data: Any = None) -> None:
        """Initialize response."""
        self.topic = topic
        self.status = status
        self.data = data
