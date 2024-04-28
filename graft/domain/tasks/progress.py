"""Progress and associated classes/exceptions."""

import enum


class Progress(enum.Enum):
    """Progress of a task."""

    NOT_STARTED = "not started"
    IN_PROGRESS = "in progress"
    COMPLETED = "completed"
