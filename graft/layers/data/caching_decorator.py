import copy
import logging
from typing import Final, override

from graft import architecture, domain
from graft.domain import tasks

logger: Final = logging.getLogger(__name__)


class CachingDecoratorDataLayer(architecture.DataLayer):
    """Data layer that returns cached values where possible.

    When a load method is called, delegate to the handler and store the returned
    value in the cache. The next time the load method is called, return the
    cached value immediately.

    When a save method is called, delegate to the handler and clear the cache.
    """

    def __init__(self, handler: architecture.DataLayer) -> None:
        """Initialise CachingDecoratorDataLayer."""
        self._handler = handler
        self._cached_next_unused_task: tasks.UID | None = None
        self._cached_system: domain.System | None = None

    @override
    def load_next_unused_task(self) -> tasks.UID:
        """Load the next unused task UID.

        "Unused" means that the UID has never been used in the system before,
        regardless of whether the task had subsequently been deleted.

        Loading an unused task UID will not add it to the system, and will
        return the same value if called multiple times. The returned value will
        only change once a system containing the task uid is saved.
        """
        if self._cached_next_unused_task is not None:
            logger.debug("Next unused task cache hit")
            return self._cached_next_unused_task

        logger.debug("Next unused task cache miss")
        self._cached_next_unused_task = self._handler.load_next_unused_task()
        return self._cached_next_unused_task

    @override
    def load_system(self) -> domain.System:
        """Load the state of the system."""
        # TODO: Improve deep copy performance by implementing deep-copy dunder
        # for record-style classes (Name, Description, etc)
        if self._cached_system is not None:
            logger.debug("System cache hit")
            return copy.deepcopy(self._cached_system)

        logger.debug("System cache miss")
        self._cached_system = self._handler.load_system()
        return copy.deepcopy(self._cached_system)

    @override
    def erase(self) -> None:
        """Erase all data."""
        self._handler.erase()
        self._clear_cache()

    @override
    def save_system(self, system: domain.System) -> None:
        """Save the state of the system."""
        self._handler.save_system(system)
        self._clear_cache()

    @override
    def save_system_and_indicate_task_used(
        self, system: domain.System, used_task: tasks.UID
    ) -> None:
        """Save the state of the system and indicate that a new task has been added."""
        self._handler.save_system_and_indicate_task_used(system, used_task)
        self._clear_cache()

    def _clear_cache(self) -> None:
        """Clear the cache."""
        self._cached_next_unused_task = None
        self._cached_system = None
