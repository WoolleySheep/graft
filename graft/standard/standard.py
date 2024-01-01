"""Standard logic-layer implementation and associated exceptions."""

from typing import override

from graft import architecture
from graft.domain import tasks
from graft.domain.tasks.dependency_graph import DependencyGraphView
from graft.domain.tasks.hierarchy_graph import HierarchyGraphView
from graft.domain.tasks.uid import UID


class StandardLogicLayer(architecture.LogicLayer):
    """Standard logic layer."""

    def __init__(self, data_layer: architecture.DataLayer) -> None:
        """Initialise StandardLogicLayer."""
        super().__init__(data_layer=data_layer)

    @override
    def initialise(self) -> None:
        """Initialise the standard logic layer, as well as the underlying data-layer."""
        self._data_layer.initialise()

    @override
    def create_task(self) -> tasks.UID:
        """Create a new task."""
        uid = self._data_layer.get_next_task_uid()
        system = self._data_layer.load_system()
        system.add_task(uid)
        self._data_layer.save_system(system=system)
        self._data_layer.increment_next_task_uid_counter()
        return uid

    @override
    def delete_task(self, task: tasks.UID) -> None:
        """Delete a task."""
        system = self._data_layer.load_system()
        system.remove_task(task)
        self._data_layer.save_system(system=system)

    @override
    def get_task_attributes_register_view(self) -> tasks.AttributesRegisterView:
        """Return a view of the task attributes register."""
        return tasks.AttributesRegisterView(
            self._data_layer.load_task_attributes_register()
        )

    @override
    def get_hierarchy_graph_view(self) -> tasks.HierarchyGraphView:
        """Return a view of the hierarchy graph."""
        return tasks.HierarchyGraphView(self._data_layer.load_task_hierarchy_graph())
    
    @override
    def get_dependency_graph_view(self) -> DependencyGraphView:
        return tasks.DependencyGraphView(self._data_layer.load_task_dependency_graph())

    @override
    def create_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Create a new hierarchy between the specified tasks."""
        system = self._data_layer.load_system()
        system.add_hierarchy(supertask=supertask, subtask=subtask)
        self._data_layer.save_system(system=system)

    @override
    def delete_hierarchy(self, supertask: UID, subtask: UID) -> None:
        """Delete the specified hierarchy."""
        system = self._data_layer.load_system()
        system.remove_hierarchy(supertask=supertask, subtask=subtask)
        self._data_layer.save_system(system=system)

    @override
    def create_dependency(self, dependee_task: UID, dependent_task: UID) -> None:
        """Create a new dependency between the specified tasks."""
        system = self._data_layer.load_system()
        system.add_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )
        self._data_layer.save_system(system=system)

    @override
    def delete_dependency(self, dependee_task: UID, dependent_task: UID) -> None:
        """Delete the specified dependency."""
        system = self._data_layer.load_system()
        system.remove_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )
        self._data_layer.save_system(system=system)
