"""System and associated classes/exceptions."""

from __future__ import annotations

from graft.domain import tasks


class System:
    """Interface for all event and task management.

    Yes, this is a bit of a god object. But there's a lot of state to manage.
    """

    @classmethod
    def empty(cls) -> System:
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
        return isinstance(other, System) and self.task_system() == other.task_system()

    def task_system(self) -> tasks.SystemView:
        """Return a view of the task system."""
        return tasks.SystemView(self._task_system)

    def add_task(self, task: tasks.UID) -> None:
        """Add a task."""
        self._task_system.add_task(task)

    def remove_task(self, task: tasks.UID) -> None:
        """Remove a task."""
        self._task_system.remove_task(task)

    def set_task_name(self, task: tasks.UID, name: tasks.Name) -> None:
        """Set the name of the specified task."""
        self._task_system.set_name(task, name)

    def set_task_description(
        self, task: tasks.UID, description: tasks.Description
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

    def get_active_concrete_tasks_in_order_of_descending_priority(
        self,
    ) -> list[tuple[tasks.UID, tasks.Importance | None]]:
        """Return the active concrete tasks in order of descending priority.

        Tasks are paired with the maximum importance of downstream tasks.
        """
        return self._task_system.get_active_concrete_tasks_in_order_of_descending_priority()
