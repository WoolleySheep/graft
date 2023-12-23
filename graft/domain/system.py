from graft.domain import event, task
from graft.domain.links import Links


class System:
    """Interface for all event and task management.

    Yes, this is a bit of a god object. But there's a lot of state to manage.
    """

    def __init__(
        self, task_network: task.Network, event_register: event.Register, links: Links
    ) -> None:
        """Initialise System"""
        self._task_network = task_network
        self._event_register = event_register
        self._links = links

    @property
    def task_register_view(self) -> task.RegisterView:
        """Return a view of the task register."""
        return self._task_network.register_view

    @property
    def event_register_view(self) -> event.RegisterView:
        """Return a view of the event register."""
        return self._event_register

    def task_hierarchies_view(self) -> task.HierarchyView:
        """Return a view of task hierarchies."""
        raise NotImplementedError

    def task_dependencies(self) -> task.HierarchyView:
        """Return a view of task hierarchies."""
        raise NotImplementedError

    def add_task(self, uid: task.UID) -> None:
        """Add a task."""
        self._task_network.add_task(uid)
