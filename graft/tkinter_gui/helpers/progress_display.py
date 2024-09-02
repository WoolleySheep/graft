from typing import Final

from graft.domain import tasks

_FORMATTED_PROGRESS_NOT_STARTED: Final = "not started"
_FORMATTED_PROGRESS_IN_PROGRESS: Final = "in progress"
_FORMATTED_PROGRESS_COMPLETED: Final = "completed"


def format(progress: tasks.Progress) -> str:
    """Format the progress as how it should appear in the GUI."""
    match progress:
        case tasks.Progress.NOT_STARTED:
            return _FORMATTED_PROGRESS_NOT_STARTED
        case tasks.Progress.IN_PROGRESS:
            return _FORMATTED_PROGRESS_IN_PROGRESS
        case tasks.Progress.COMPLETED:
            return _FORMATTED_PROGRESS_COMPLETED


def parse(formatted_progress: str) -> tasks.Progress:
    """Parse how the progress appears in the GUI back to its canonical form.

    Case-agnostic.
    """
    lowercase_formatted_progress = formatted_progress.lower()

    if lowercase_formatted_progress == _FORMATTED_PROGRESS_NOT_STARTED:
        return tasks.Progress.NOT_STARTED

    if lowercase_formatted_progress == _FORMATTED_PROGRESS_IN_PROGRESS:
        return tasks.Progress.IN_PROGRESS

    if lowercase_formatted_progress == _FORMATTED_PROGRESS_COMPLETED:
        return tasks.Progress.COMPLETED

    raise ValueError(f"Unknown progress: {formatted_progress}")
