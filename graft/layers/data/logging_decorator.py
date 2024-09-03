import logging
from typing import Final, override

from graft import architecture, domain
from graft.domain import tasks

logger: Final = logging.getLogger(__name__)


class LoggingDecoratorDataLayer(architecture.DataLayer):
    """Data layer that logs method calls and passes to a handler."""

    def __init__(self, handler: architecture.DataLayer) -> None:
        """Initialise LoggingDecoratorDataLayer."""
        logger.info("Initialising %s", self.__class__.__name__)
        self._handler = handler
        logger.info("Initialised %s", self.__class__.__name__)

    @override
    def load_next_unused_task(self) -> tasks.UID:
        """Load the next unused task UID.

        "Unused" means that the UID has never been used in the system before,
        regardless of whether the task had subsequently been deleted.

        Loading an unused task UID will not add it to the system, and will
        return the same value if called multiple times. The returned value will
        only change once a system containing the task uid is saved.
        """
        logger.debug("Loading next unused task UID")
        try:
            next_unused_task = self._handler.load_next_unused_task()
        except Exception as e:
            logger.error("Failed to load next unused task ID, exception [%s]", e)
            raise
        logger.debug("Next unused task UID [%s] loaded", next_unused_task)
        return next_unused_task

    @override
    def load_system(self) -> domain.System:
        """Load the state of the system."""
        logger.debug("Loading system")
        try:
            system = self._handler.load_system()
        except Exception as e:
            logger.error("Failed to load system, exception [%s]", e)
            raise
        logger.debug("System loaded")
        return system

    @override
    def erase(self) -> None:
        """Erase all data."""
        logger.info("Erasing data")
        try:
            self._handler.erase()
        except Exception as e:
            logger.error("Failed to erase data, exception [%s]", e)
            raise
        logger.info("Data erased")

    @override
    def save_system(self, system: domain.ISystemView) -> None:
        """Save the state of the system."""
        logger.info("Saving system")
        try:
            self._handler.save_system(system)
        except Exception as e:
            logger.error("Failed to save system, exception [%s]", e)
            raise
        logger.info("System saved")

    @override
    def save_system_and_indicate_task_used(
        self, system: domain.ISystemView, used_task: tasks.UID
    ) -> None:
        """Save the state of the system and indicate that a new task has been added."""
        logger.info("Saving system and indicating task with UID [%s] used", used_task)
        try:
            self._handler.save_system_and_indicate_task_used(system, used_task)
        except Exception as e:
            logger.error(
                "Failed to save system and indicate task with UID [%s] used, exception [%s]",
                used_task,
                e,
            )
            raise
        logger.info("System saved and task with UID [%s] marked as used", used_task)
