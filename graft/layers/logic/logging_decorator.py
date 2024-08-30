import logging
from typing import Final, override

from graft import architecture
from graft.domain import tasks

logger: Final = logging.getLogger(__name__)


class LoggingDecoratorLogicLayer(architecture.LogicLayer):
    """Logic layer that logs method calls and passes to a handler."""

    def __init__(self, handler: architecture.LogicLayer) -> None:
        """Initialise LoggingDecoratorLogicLayer."""
        logger.info("Initialising %s", self.__class__.__name__)
        self._handler = handler
        logger.info("Initialised %s", self.__class__.__name__)

    @override
    def erase(self) -> None:
        logger.info("Erasing all data")
        try:
            self._data_layer.erase()
        except Exception as e:
            logger.warning("Failed to erase all data, exception [%s]", e)
            raise

        logger.info("All data erased")

    @override
    def create_task(
        self,
        name: tasks.Name | None = None,
        description: tasks.Description | None = None,
    ) -> tasks.UID:
        """Create a new task."""
        match (name, description):
            case (None, None):
                logger.info("Creating new task")
            case (None, _):
                logger.info("Creating new task with description [%s]", description)
            case (_, None):
                logger.info("Creating new task with name [%s]", name)
            case (_, _):
                logger.info(
                    "Creating new task with name [%s] and description [%s]",
                    name,
                    description,
                )

        try:
            new_task = self._handler.create_task(name=name, description=description)
        except Exception as e:
            match (name, description):
                case (None, None):
                    logger.warning("Failed to create new task, exception [%s]", e)
                case (None, _):
                    logger.warning(
                        "Failed to create new task with description [%s], exception [%s]",
                        description,
                        e,
                    )
                case (_, None):
                    logger.warning(
                        "Failed to create new task with name [%s], exception [%s]",
                        name,
                        e,
                    )
                case (_, _):
                    logger.warning(
                        "Failed to create new task with name [%s] and description [%s], exception [%s]",
                        name,
                        description,
                        e,
                    )
            raise

        match (name, description):
            case (None, None):
                logger.info("New task created, assigned UID [%s]", new_task)
            case (None, _):
                logger.info(
                    "New task created with description [%s], assigned UID [%s]",
                    description,
                    new_task,
                )
            case (_, None):
                logger.info(
                    "New task created with name [%s], assigned UID [%s]", name, new_task
                )
            case (_, _):
                logger.info(
                    "New task created with name [%s] and description [%s], assigned UID [%s]",
                    name,
                    description,
                    new_task,
                )

        return new_task

    @override
    def get_next_unused_task(self) -> tasks.UID:
        logger.debug("Getting next unused task UID")
        try:
            next_unused_task = self._handler.get_next_unused_task()
        except Exception as e:
            logger.warning("Failed to get next unused task UID, exception [%s]", e)
            raise
        logger.debug("Got next unused task UID [%s]", next_unused_task)
        return next_unused_task

    @override
    def delete_task(self, task: tasks.UID) -> None:
        """Delete a task."""
        logger.info("Deleting task with UID [%s]", task)
        try:
            self._handler.delete_task(task)
        except Exception as e:
            logger.warning(
                "Failed to delete task with UID [%s], exception [%s]", task, e
            )
            raise
        logger.info("Task with UID [%s] deleted", task)

    @override
    def update_task_name(self, task: tasks.UID, name: tasks.Name) -> None:
        """Update the specified task's name."""
        logger.info("Updating name of task with UID [%s] to [%s]", task, name)
        try:
            self._handler.update_task_name(task, name)
        except Exception as e:
            logger.warning(
                "Failed to update name of task with UID [%s] to [%s], exception [%s]",
                task,
                name,
                e,
            )
            raise
        logger.info("Name of task with UID [%s] updated to [%s]", task, name)

    @override
    def update_task_description(
        self, task: tasks.UID, description: tasks.Description
    ) -> None:
        """Update the specified task's description."""
        logger.info(
            "Updating description of task with UID [%s] to [%s]", task, description
        )
        try:
            self._handler.update_task_description(task, description)
        except Exception as e:
            logger.warning(
                "Failed to update description of task with UID [%s] to [%s], exception [%s]",
                task,
                description,
                e,
            )
            raise
        logger.info(
            "Description of task with UID [%s] updated to [%s]", task, description
        )

    @override
    def update_concrete_task_progress(
        self, task: tasks.UID, progress: tasks.Progress
    ) -> None:
        """Update the specified concrete task's progress."""
        logger.info(
            "Updating progress of task with UID [%s] to [%s]", task, progress.value
        )
        try:
            self._handler.update_concrete_task_progress(task, progress)
        except Exception as e:
            logger.warning(
                "Failed to update progress of task with UID [%s] to [%s], exception [%s]",
                task,
                progress.value,
                e,
            )
            raise
        logger.info(
            "Progress of task with UID [%s] updated to [%s]", task, progress.value
        )

    @override
    def update_task_importance(
        self, task: tasks.UID, importance: tasks.Importance | None = None
    ) -> None:
        """Update the specified task's importance."""
        match importance:
            case None:
                logger.info("Removing importance of task with UID [%s]", task)
            case _:
                logger.info(
                    "Updating importance of task with UID [%s] to [%s]",
                    task,
                    importance.value,
                )
        try:
            self._handler.update_task_importance(task, importance)
        except Exception as e:
            match importance:
                case None:
                    logger.info(
                        "Failed to remove importance of task with UID [%s], exception [%s]",
                        task,
                        e,
                    )
                case _:
                    logger.info(
                        "Failed to update importance of task with UID [%s] to [%s], exception [%s]",
                        task,
                        importance.value,
                        e,
                    )
            raise

        match importance:
            case None:
                logger.info("Importance of task with UID [%s] removed", task)
            case _:
                logger.info(
                    "Importance of task with UID [%s] updated to [%s]",
                    task,
                    importance.value,
                )

    @override
    def get_task_system(self) -> tasks.SystemView:
        """Return a view of the system."""
        logger.debug("Getting task system")
        try:
            task_system = self._handler.get_task_system()
        except Exception as e:
            logger.warning("Failed to get task system, exception [%s]", e)
            raise
        logger.debug("Got task system")
        return task_system

    @override
    def create_task_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Create a new hierarchy between the specified tasks."""
        logger.info(
            "Creating hierarchy between supertask with UID [%s] and subtask with UID [%s]",
            supertask,
            subtask,
        )
        try:
            self._handler.create_task_hierarchy(supertask, subtask)
        except Exception as e:
            logger.warning(
                "Failed to create hierarchy between supertask with UID [%s] and subtask with UID [%s], exception [%s]",
                supertask,
                subtask,
                e,
            )
            raise
        logger.info(
            "Hierarchy created between supertask with UID [%s] and subtask with UID [%s]",
            supertask,
            subtask,
        )

    @override
    def delete_task_hierarchy(self, supertask: tasks.UID, subtask: tasks.UID) -> None:
        """Delete the specified hierarchy."""
        logger.info(
            "Deleting hierarchy between supertask with UID [%s] and subtask with UID [%s]",
            supertask,
            subtask,
        )
        try:
            self._handler.delete_task_hierarchy(supertask, subtask)
        except Exception as e:
            logger.warning(
                "Failed to delete hierarchy between supertask with UID [%s] and subtask with UID [%s], exception [%s]",
                supertask,
                subtask,
                e,
            )
            raise
        logger.info(
            "Hierarchy deleted between supertask with UID [%s] and subtask with UID [%s]",
            supertask,
            subtask,
        )

    @override
    def create_task_dependency(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> None:
        """Create a new dependency between the specified tasks."""
        logger.info(
            "Creating dependency between dependee-task with UID [%s] and dependent-task with UID [%s]",
            dependee_task,
            dependent_task,
        )
        try:
            self._handler.create_task_dependency(dependee_task, dependent_task)
        except Exception as e:
            logger.warning(
                "Failed to create dependency between dependee-task with UID [%s] and dependent-task with UID [%s], exception [%s]",
                dependee_task,
                dependent_task,
                e,
            )
            raise
        logger.info(
            "Dependency created between dependee-task with UID [%s] and dependent-task with UID [%s]",
            dependee_task,
            dependent_task,
        )

    @override
    def delete_task_dependency(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> None:
        """Delete the specified dependency."""
        logger.info(
            "Deleting dependency between dependee-task with UID [%s] and dependent-task with UID [%s]",
            dependee_task,
            dependent_task,
        )
        try:
            self._handler.delete_task_dependency(dependee_task, dependent_task)
        except Exception as e:
            logger.warning(
                "Failed to delete dependency between dependee-task with UID [%s] and dependent-task with UID [%s], exception [%s]",
                dependee_task,
                dependent_task,
                e,
            )
            raise
        logger.info(
            "Dependency deleted between dependee-task with UID [%s] and dependent-task with UID [%s]",
            dependee_task,
            dependent_task,
        )

    @override
    def get_active_concrete_tasks_in_order_of_descending_priority(
        self,
    ) -> list[tuple[tasks.UID, tasks.Importance | None]]:
        """Return the active concrete tasks in order of descending priority.

        Tasks are paired with the maximum importance of downstream tasks.
        """
        logger.debug("Getting active concrete tasks in order of descending priority")
        try:
            active_concrete_tasks_in_order_of_descending_priority = self._handler.get_active_concrete_tasks_in_order_of_descending_priority()
        except Exception as e:
            logger.warning(
                "Failed to get active concrete tasks in order of descending priority, exception [%s]",
                e,
            )
            raise
        logger.debug("Got active concrete tasks in order of descending priority")
        return active_concrete_tasks_in_order_of_descending_priority
