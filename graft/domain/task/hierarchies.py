from collections.abc import Iterable
from typing import Any

from graft import graph
from graft.domain.task import task


class PartOfAHierarchyError(Exception):
    """Raised when node is part of a hierarchy."""

    def __init__(
        self,
        uid: task.UID,
        subtasks: Iterable[task.UID],
        supertasks: Iterable[task.UID],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize HasEdgesError."""
        self.uid = uid
        self.subtasks = set(subtasks)
        self.supertasks = set(supertasks)
        super().__init__(f"task [{task}] is part of a hierarchy", *args, **kwargs)


class Hierarchies:
    """Task Hierarchies.

    Acts as a Minimum DAG.
    """

    def __init__(self, minimum_dag: graph.MinimumDAG[task.UID]) -> None:
        """Initialise Hierarchies."""
        self._minimum_dag = minimum_dag

    def add_task(self, /, uid: task.UID) -> None:
        """Add a task."""
        try:
            self._minimum_dag.add_node(uid)
        except graph.NodeAlreadyExistsError as e:
            raise task.UIDAlreadyExistsError(uid) from e
        except Exception as e:
            raise e

    def remove_task(self, /, uid: task.UID) -> None:
        """Remove a task."""
        try:
            self._minimum_dag.remove_node(uid)
        except graph.NodeDoesNotExistError as e:
            raise task.UIDDoesNotExistError(uid=uid) from e
        except graph.HasEdgesError as e:
            raise PartOfAHierarchyError(
                uid=uid, subtasks=e.successors, supertasks=e.predecessors
            ) from e
        except Exception as e:
            raise e
