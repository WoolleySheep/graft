from collections.abc import Iterator

from graft.domain.task import task
from graft.domain.task.dependencies import Dependencies
from graft.domain.task.hierarchies import Hierarchies
from graft.domain.task.register import Register, RegisterView


class Network:
    """Task network."""

    def __init__(
        self, register: Register, hierarchies: Hierarchies, dependencies: Dependencies
    ) -> None:
        self._register = register
        self._hierarchies = hierarchies
        self._dependencies = dependencies

    @property
    def register_view(self) -> RegisterView:
        """Return a view of the task register."""
        return self._register

    def hierarchies_view(self) -> task.HierarchiesView:
        """Return a mapping of task views, showing hierarchies."""
        raise NotImplementedError

    def dependencies_view(self) -> task.DependenciesView:
        """Return a mapping of task views, showing dependencies."""
        raise NotImplementedError

    def __contains__(self, key: task.UID) -> bool:
        """Return True if key is in the task network."""
        return key in self._register

    def __iter__(self) -> Iterator[task.UID]:
        """Iterate over the task UIDs in the network."""
        return iter(self._register)

    def add_task(self, /, uid: task.UID) -> None:
        """Add a task."""
        self._register.add(uid)
        self._hierarchies.add_task(uid)
        self._dependencies.add_task(uid)
