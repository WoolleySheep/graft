"""Importance and associated classes/exceptions."""

import enum


class Importance(enum.Enum):
    """Importance of a task."""

    LOW = enum.auto()
    MEDIUM = enum.auto()
    HIGH = enum.auto()

    def __lt__(self, other: object) -> bool:
        """Check if a task's importance is less than another's.

        LOW < MEDIUM < HIGH
        """
        if not isinstance(other, Importance):
            raise NotImplementedError

        match self:
            case Importance.LOW:
                return other is not Importance.LOW
            case Importance.MEDIUM:
                return other is Importance.HIGH
            case Importance.HIGH:
                return False
