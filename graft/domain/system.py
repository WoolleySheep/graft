"""System and associated classes/exceptions."""

from collections.abc import Generator
from typing import Self

from graft.domain import tasks


class System:
    """Interface for all event and task management.

    Yes, this is a bit of a god object. But there's a lot of state to manage.
    """

    @classmethod
    def empty(cls) -> Self:
        """Create an empty system."""
        return cls(task_system=tasks.System.empty())

    def __init__(
        self,
        task_system: tasks.System,
    ) -> None:
        """Initialise System."""
        self._task_system = task_system

    def __eq__(self, other: object) -> bool:
        """Check if two systems are equal."""
        return (
            isinstance(other, System)
            and self.task_system_view() == other.task_system_view()
        )

    def task_system_view(self) -> tasks.SystemView:
        """Return a view of the task system."""
        return tasks.SystemView(self._task_system)

    def add_task(self, task: tasks.UID) -> None:
        """Add a task."""
        self._task_system.add_task(task)

    def remove_task(self, task: tasks.UID) -> None:
        """Remove a task."""
        self._task_system.remove_task(task)

    def set_task_name(self, task: tasks.UID, name: tasks.Name | None = None) -> None:
        """Set the name of the specified task."""
        self._task_system.set_name(task, name)

    def set_task_description(
        self, task: tasks.UID, description: tasks.Description | None = None
    ) -> None:
        """Set the description of the specified task."""
        self._task_system.set_description(task, description)

    def set_task_progress(self, task: tasks.UID, progress: tasks.Progress) -> None:
        """Set the progress of the specified task."""
        self._task_system.set_progress(task, progress)

    def set_task_importance(
        self, task: tasks.UID, importance: tasks.Importance | None = None
    ) -> None:
        """Set the importance of the specified task."""
        self._task_system.set_importance(task, importance)

    def add_task_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Add a hierarchy between the specified tasks."""
        self._task_system.add_hierarchy(supertask, subtask)

    def remove_task_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Remove a hierarchy between the specified tasks."""
        self._task_system.remove_hierarchy(supertask=supertask, subtask=subtask)

    def add_task_dependency(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> None:
        """Add a dependency between the specified tasks."""
        self._task_system.add_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )

    def remove_task_dependency(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> None:
        """Remove a dependency between the specified tasks."""
        self._task_system.remove_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )

    def get_active_concrete_tasks_in_priority_order(
        self,
    ) -> Generator[tasks.UID, None, None]:
        """Return the active concrete tasks in priority order."""
        return self._task_system.get_active_concrete_tasks_in_priority_order()
