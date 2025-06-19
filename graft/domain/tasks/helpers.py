"""Exceptions that don't logically live anywhere else."""

import contextlib
from collections.abc import Generator
from typing import Any

from graft import graphs
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


@contextlib.contextmanager
def reraise_node_does_not_exist_as_task_does_not_exist() -> Generator[None, None, None]:
    """Reraise NodeDoesNotExistError as TaskDoesNotExistError."""
    try:
        yield
    except graphs.NodeDoesNotExistError as e:
        assert isinstance(e.node, UID)
        raise TaskDoesNotExistError(e.node) from e


@contextlib.contextmanager
def reraise_node_already_exists_as_task_already_exists() -> Generator[None, None, None]:
    """Reraise NodeAlreadyExistsError as TaskAlreadyExistsError."""
    try:
        yield
    except graphs.NodeAlreadyExistsError as e:
        assert isinstance(e.node, UID)
        raise TaskAlreadyExistsError(e.node) from e
