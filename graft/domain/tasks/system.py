"""System and associated classes/exceptions."""

from collections.abc import Iterator

from graft.domain.tasks.attributes_register import (
    AttributesRegister,
    AttributesRegisterView,
)
from graft.domain.tasks.dependency_graph import DependencyGraph, DependencyGraphView
from graft.domain.tasks.hierarchy_graph import HierarchyGraph, HierarchyGraphView
from graft.domain.tasks.uid import UID


class System:
    """System of task information."""

    def __init__(
        self,
        attributes_register: AttributesRegister,
        hierarchy_graph: HierarchyGraph,
        dependency_graph: DependencyGraph,
    ) -> None:
        """Initialise System."""
        self._attributes_register = attributes_register
        self._hierarchy_graph = hierarchy_graph
        self._dependency_graph = dependency_graph

    def attributes_register_view(self) -> AttributesRegisterView:
        """Return a view of the attributes register."""
        return AttributesRegisterView(self._attributes_register)

    def hierarchy_graph_view(self) -> HierarchyGraphView:
        """Return a view of the hierarchy graph."""
        return HierarchyGraphView(self._hierarchy_graph)

    def dependency_graph_view(self) -> DependencyGraphView:
        """Return a view of the dependency graph."""
        return DependencyGraphView(self._dependency_graph)

    def __bool__(self) -> bool:
        """Return True if the system is not empty."""
        return bool(self._attributes_register)

    def __contains__(self, key: UID) -> bool:
        """Return True if key is in the task network."""
        return key in self._attributes_register

    def __iter__(self) -> Iterator[UID]:
        """Iterate over the task UIDs in the network."""
        return iter(self._attributes_register)

    def add_task(self, /, task: UID) -> None:
        """Add a task."""
        self._attributes_register.add(task)
        self._hierarchy_graph.add_task(task)
        self._dependency_graph.add_task(task)


class SystemView:
    """View of System."""

    def __init__(self, system: System) -> None:
        """Initialise SystemView."""
        self._system = system

    def attributes_register_view(self) -> AttributesRegisterView:
        """Return a view of the attributes register."""
        return self._system.attributes_register_view()

    def hierarchy_graph_view(self) -> HierarchyGraphView:
        """Return a view of the hierarchy graph."""
        return self._system.hierarchy_graph_view()

    def dependency_graph_view(self) -> DependencyGraphView:
        """Return a view of the dependency graph."""
        return self._system.dependency_graph_view()
