"""Progress and associated classes/exceptions."""

import enum


class Progress(enum.Enum):
    """Progress of a task."""

    NOT_STARTED = enum.auto()
    IN_PROGRESS = enum.auto()
    COMPLETED = enum.auto()

    def __lt__(self, other: object) -> bool:
        """Check if a task's progress is less than another's.

        NOT_STARTED < IN_PROGRESS < COMPLETED
        """
        if not isinstance(other, Progress):
            raise NotImplementedError

        match self:
            case Progress.NOT_STARTED:
                return other is not Progress.NOT_STARTED
            case Progress.IN_PROGRESS:
                return other is Progress.COMPLETED
            case Progress.COMPLETED:
                return False
