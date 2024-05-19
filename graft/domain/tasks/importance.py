"""Importance and associated classes/exceptions."""

import enum


class Importance(enum.Enum):
    """Importance of a task."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Importance):
            raise NotImplementedError

        match self:
            case Importance.LOW:
                return other is not Importance.LOW
            case Importance.MEDIUM:
                return other is Importance.HIGH
            case Importance.HIGH:
                return False
