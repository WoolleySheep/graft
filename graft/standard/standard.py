"""Standard logic-layer implementation and associated exceptions."""

from typing import override

from graft import architecture
from graft.domain import tasks


class StandardLogicLayer(architecture.LogicLayer):
    """Standard logic layer."""

    def __init__(self, data_layer: architecture.DataLayer) -> None:
        """Initialise StandardLogicLayer."""
        super().__init__(data_layer=data_layer)
        self._system = self._data_layer.load_system()

    @override
    def create_task(self) -> tasks.UID:
        """Create a new task."""
        uid = self._data_layer.get_next_task_uid()
        self._system.add_task(uid)
        self._data_layer.save_system(system=self._system)
        self._data_layer.increment_next_task_uid_counter()
        return uid

    @override
    def delete_task(self, task: tasks.UID) -> None:
        """Delete a task."""
        self._system.remove_task(task)
        self._data_layer.save_system(system=self._system)

    @override
    def get_task_attributes_register_view(self) -> tasks.AttributesRegisterView:
        """Return a view of the task attributes register."""
        return self._system.task_system_view().attributes_register_view()

    @override
    def get_hierarchy_graph_view(self) -> tasks.HierarchyGraphView:
        """Return a view of the hierarchy graph."""
        return self._system.task_system_view().hierarchy_graph_view()

    @override
    def get_dependency_graph_view(self) -> tasks.DependencyGraphView:
        return self._system.task_system_view().dependency_graph_view()

    @override
    def create_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Create a new hierarchy between the specified tasks."""
        self._system.add_hierarchy(supertask=supertask, subtask=subtask)
        self._data_layer.save_system(system=self._system)

    @override
    def delete_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Delete the specified hierarchy."""
        self._system.remove_hierarchy(supertask=supertask, subtask=subtask)
        self._data_layer.save_system(system=self._system)

    @override
    def create_dependency(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> None:
        """Create a new dependency between the specified tasks."""
        self._system.add_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )
        self._data_layer.save_system(system=self._system)

    @override
    def delete_dependency(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> None:
        """Delete the specified dependency."""
        self._system.remove_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )
        self._data_layer.save_system(system=self._system)
