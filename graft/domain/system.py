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

    def __eq__(self, other: object) -> bool:
        """Check if two systems are equal."""
        if not isinstance(other, System):
            return False

        return self.task_system_view() == other.task_system_view()

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

    def add_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Add a hierarchy between the specified tasks."""
        self._task_system.add_hierarchy(supertask, subtask)

    def remove_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Remove a hierarchy between the specified tasks."""
        self._task_system.remove_hierarchy(supertask=supertask, subtask=subtask)

    def add_dependency(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> None:
        """Add a dependency between the specified tasks."""
        self._task_system.add_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )

    def remove_dependency(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> None:
        """Remove a dependency between the specified tasks."""
        self._task_system.remove_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )
