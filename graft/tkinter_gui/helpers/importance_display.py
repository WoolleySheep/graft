from typing import Final

from graft.domain import tasks

_FORMATTED_IMPORTANCE_LOW: Final = "low"
_FORMATTED_IMPORTANCE_MEDIUM: Final = "medium"
_FORMATTED_IMPORTANCE_HIGH: Final = "high"


def format(importance: tasks.Importance) -> str:
    """Format the importance as how it should appear in the GUI."""
    match importance:
        case tasks.Importance.LOW:
            return _FORMATTED_IMPORTANCE_LOW
        case tasks.Importance.MEDIUM:
            return _FORMATTED_IMPORTANCE_MEDIUM
        case tasks.Importance.HIGH:
            return _FORMATTED_IMPORTANCE_HIGH


def parse(formatted_importance: str) -> tasks.Importance:
    """Parse how the importance appears in the GUI back to its canonical form.

    Case-agnostic.
    """
    lowercase_formatted_importance = formatted_importance.lower()

    if lowercase_formatted_importance == _FORMATTED_IMPORTANCE_LOW:
        return tasks.Importance.LOW

    if lowercase_formatted_importance == _FORMATTED_IMPORTANCE_MEDIUM:
        return tasks.Importance.MEDIUM

    if lowercase_formatted_importance == _FORMATTED_IMPORTANCE_HIGH:
        return tasks.Importance.HIGH

    raise ValueError(f"Unknown importance: {formatted_importance}")
