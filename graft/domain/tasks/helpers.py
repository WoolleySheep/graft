"""Exceptions that don't logically live anywhere else."""

from typing import Any

from graft.domain.tasks.uid import UID


class TaskAlreadyExistsError(Exception):
    """Raised when the task already exists."""

    def __init__(
        self,
        task: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize TaskAlreadyExistsError."""
        self.task = task
        super().__init__(f"task with UID [{task}] already exists", *args, **kwargs)


class TaskDoesNotExistError(Exception):
    """Raised when task does not exist."""

    def __init__(
        self,
        task: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize UIDDoesNotExistError."""
        self.task = task
        super().__init__(f"task with UID [{task}] does not exist", *args, **kwargs)
