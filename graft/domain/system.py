"""System and associated classes/exceptions."""

from graft.domain import tasks


class System:
    """Interface for all event and task management.

    Yes, this is a bit of a god object. But there's a lot of state to manage.
    """

    def __init__(
        self,
        task_system: tasks.System,
    ) -> None:
        """Initialise System."""
        self._task_system = task_system

    def task_system_view(self) -> tasks.SystemView:
        """Return a view of the task system."""
        return tasks.SystemView(self._task_system)

    def add_task(self, task: tasks.UID) -> None:
        """Add a task."""
        self._task_system.add_task(task)

    def remove_task(self, task: tasks.UID) -> None:
        """Remove a task."""
        self._task_system.remove_task(task)

    def add_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Add a hierarchy between the specified tasks."""
        self._task_system.add_hierarchy(supertask, subtask)
