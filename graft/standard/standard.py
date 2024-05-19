"""Standard logic-layer implementation and associated exceptions."""

from collections.abc import Generator
from typing import override

from graft import architecture
from graft.domain import tasks
from graft.domain.tasks.description import Description
from graft.domain.tasks.uid import UID


class StandardLogicLayer(architecture.LogicLayer):
    """Standard logic layer."""

    def __init__(self, data_layer: architecture.DataLayer) -> None:
        """Initialise StandardLogicLayer."""
        super().__init__(data_layer=data_layer)
        self._system = self._data_layer.load_system()

    @override
    def erase(self) -> None:
        self._data_layer.erase()
        self._system = self._data_layer.load_system()

    @override
    def create_task(
        self,
        name: tasks.Name | None = None,
        description: tasks.Description | None = None,
    ) -> tasks.UID:
        """Create a new task."""
        uid = self._data_layer.get_next_task_uid()
        self._system.add_task(uid)
        self._system.set_task_name(uid, name)
        self._system.set_task_description(uid, description)
        self._data_layer.save_system(system=self._system)
        self._data_layer.increment_next_task_uid_counter()
        return uid

    @override
    def get_next_task_id(self) -> UID:
        return self._data_layer.get_next_task_uid()

    @override
    def delete_task(self, task: tasks.UID) -> None:
        """Delete a task."""
        self._system.remove_task(task)
        self._data_layer.save_system(system=self._system)

    @override
    def update_task_name(self, task: tasks.UID, name: tasks.Name | None = None) -> None:
        """Update the specified task's name."""
        self._system.set_task_name(task, name)
        self._data_layer.save_system(system=self._system)

    @override
    def update_task_description(
        self, task: UID, description: Description | None = None
    ) -> None:
        """Update the specified task's description."""
        self._system.set_task_description(task, description)
        self._data_layer.save_system(system=self._system)

    @override
    def update_task_progress(self, task: UID, progress: tasks.Progress) -> None:
        """Update the specified task's progress."""
        self._system.set_task_progress(task, progress)
        self._data_layer.save_system(system=self._system)

    @override
    def update_task_importance(
        self, task: UID, importance: tasks.Importance | None = None
    ) -> None:
        """Update the specified task's importance."""
        self._system.set_task_importance(task, importance)
        self._data_layer.save_system(system=self._system)

    @override
    def get_task_attributes_register_view(self) -> tasks.AttributesRegisterView:
        """Return a view of the task attributes register."""
        return self._system.task_system_view().attributes_register_view()

    @override
    def get_task_hierarchy_graph_view(self) -> tasks.HierarchyGraphView:
        """Return a view of the hierarchy graph."""
        return self._system.task_system_view().hierarchy_graph_view()

    @override
    def get_task_dependency_graph_view(self) -> tasks.DependencyGraphView:
        return self._system.task_system_view().dependency_graph_view()

    @override
    def get_task_system_view(self) -> tasks.SystemView:
        return self._system.task_system_view()

    @override
    def create_task_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Create a new hierarchy between the specified tasks."""
        self._system.add_task_hierarchy(supertask=supertask, subtask=subtask)
        self._data_layer.save_system(system=self._system)

    @override
    def delete_task_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Delete the specified hierarchy."""
        self._system.remove_task_hierarchy(supertask=supertask, subtask=subtask)
        self._data_layer.save_system(system=self._system)

    @override
    def create_task_dependency(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> None:
        """Create a new dependency between the specified tasks."""
        self._system.add_task_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )
        self._data_layer.save_system(system=self._system)

    @override
    def delete_task_dependency(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> None:
        """Delete the specified dependency."""
        self._system.remove_task_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )
        self._data_layer.save_system(system=self._system)

    @override
    def get_active_concrete_tasks_in_priority_order(
        self,
    ) -> Generator[tasks.UID, None, None]:
        """Return the active concrete tasks in priority order."""
        return self._system.get_active_concrete_tasks_in_priority_order()
