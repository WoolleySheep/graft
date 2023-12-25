from graft.domain import task


class System:
    """Interface for all event and task management.

    Yes, this is a bit of a god object. But there's a lot of state to manage.
    """

    def __init__(
        self,
        task_system: task.System,
    ) -> None:
        """Initialise System."""
        self._task_system = task_system

    def task_system_view(self) -> task.SystemView:
        """Return a view of the task system."""
        return task.SystemView(self._task_system)

    def add_task(self, uid: task.UID) -> None:
        """Add a task."""
        self._task_system.add_task(uid)
