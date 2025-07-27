"""Standard logic-layer implementation and associated exceptions."""

import logging
from typing import Final, override

from graft import architecture, domain
from graft.domain import tasks
from graft.domain.tasks.description import Description
from graft.domain.tasks.uid import UID

logger: Final = logging.getLogger(__name__)


class StandardLogicLayer(architecture.LogicLayer):
    """Standard logic layer."""

    def __init__(self, data_layer: architecture.DataLayer) -> None:
        """Initialise StandardLogicLayer."""
        logger.info("Initialising %s", self.__class__.__name__)
        try:
            super().__init__(data_layer=data_layer)
            self._system = self._data_layer.load_system()
        except:
            logger.error("Failed to initialise %s", self.__class__.__name__)
            raise
        logger.info("Initialised %s", self.__class__.__name__)

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
        name = name if name is not None else tasks.Name()
        description = description if description is not None else tasks.Description()

        uid = self._data_layer.load_next_unused_task()
        self._system.add_task(uid)
        self._system.set_task_name(uid, name)
        self._system.set_task_description(uid, description)
        self._data_layer.save_system_and_indicate_task_used(
            system=self._system, used_task=uid
        )
        return uid

    @override
    def get_next_unused_task(self) -> UID:
        return self._data_layer.load_next_unused_task()

    @override
    def delete_task(self, task: tasks.UID) -> None:
        """Delete a task."""
        self._system.remove_task(task)
        self._data_layer.save_system(system=self._system)

    @override
    def update_task_name(self, task: tasks.UID, name: tasks.Name) -> None:
        """Update the specified task's name."""
        self._system.set_task_name(task, name)
        self._data_layer.save_system(system=self._system)

    @override
    def update_task_description(self, task: UID, description: Description) -> None:
        """Update the specified task's description."""
        self._system.set_task_description(task, description)
        self._data_layer.save_system(system=self._system)

    @override
    def update_concrete_task_progress(
        self, task: UID, progress: tasks.Progress
    ) -> None:
        """Update the specified concrete task's progress."""
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
    def get_task_system(self) -> tasks.SystemView:
        """Return a view of the system."""
        return self._system.task_system()

    def get_system(self) -> domain.SystemView:
        """Return a view of the system."""
        return domain.SystemView(self._system)

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
