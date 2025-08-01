import functools
import itertools
from collections.abc import Callable, MutableMapping

from graft.domain import tasks
from graft.domain.system import ISystemView


def get_active_concrete_tasks_in_descending_priority_order(
    system: ISystemView,
) -> list[
    tuple[tasks.UID, tasks.Importance | None, tasks.Importance | None, tasks.Progress]
]:
    """Return the active concrete tasks in order of descending priority.

    Tasks are prioritised by:
    1. The maximum importance of their downstream tasks + themselves
    2. Their own importance
    3. Their progress
    4. Their task ID (lower == better)
    """

    class PriorityScoreCard:
        """Scorecard for calculating the priority of a task.

        The general gist is that taskA is of higher priority than taskB if:
            A. Is its combined importance higher (max of own importance and highest downstream importance)
            B. It itself a higher importance
            C. It is further progressed
        """

        def __init__(
            self,
            get_importance: Callable[[], tasks.Importance | None],
            get_highest_downstream_importance: Callable[[], tasks.Importance | None],
            progress: tasks.Progress,
        ) -> None:
            self._get_importance = get_importance
            self._get_highest_downstream_importance = get_highest_downstream_importance
            self._progress = progress

        @property
        def importance(self) -> tasks.Importance | None:
            return self._get_importance()

        @property
        def _highest_downstream_importance(self) -> tasks.Importance | None:
            return self._get_highest_downstream_importance()

        @property
        def progress(self) -> tasks.Progress:
            return self._progress

        @property
        def combined_importance(self) -> tasks.Importance | None:
            if self.importance is None:
                return self._highest_downstream_importance

            if self._highest_downstream_importance is None:
                return self.importance

            if self.importance is tasks.Importance.HIGH:
                return self.importance

            return max(self.importance, self._highest_downstream_importance)

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, PriorityScoreCard):
                return NotImplemented

            return (
                self.combined_importance is other.combined_importance
                and self.importance is other.importance
                and self.progress is other.progress
            )

        def __lt__(self, other: object) -> bool:
            if not isinstance(other, PriorityScoreCard):
                return NotImplemented

            return bool(
                (not self.combined_importance and other.combined_importance)
                or (
                    self.combined_importance
                    and other.combined_importance
                    and self.combined_importance < other.combined_importance
                )
                or (
                    self.combined_importance is other.combined_importance
                    and (
                        (
                            (not self.importance and other.importance)
                            or (
                                self.importance
                                and other.importance
                                and self.importance < other.importance
                            )
                        )
                        or (
                            self.importance is other.importance
                            and self.progress < other.progress
                        )
                    )
                )
            )

    def get_progress_recursive(
        task: tasks.UID,
        system: tasks.ISystemView,
        task_to_progress_map: MutableMapping[tasks.UID, tasks.Progress],
    ) -> tasks.Progress:
        if system.network_graph().hierarchy_graph().is_concrete(task):
            return system.get_progress(task)

        if task in task_to_progress_map:
            return task_to_progress_map[task]

        progress: tasks.Progress | None = None
        for subtask in system.network_graph().hierarchy_graph().subtasks(task):
            subtask_progress = get_progress_recursive(
                subtask, system, task_to_progress_map
            )

            match subtask_progress:
                case tasks.Progress.NOT_STARTED:
                    if progress is tasks.Progress.COMPLETED:
                        progress = tasks.Progress.IN_PROGRESS
                        break
                    progress = tasks.Progress.NOT_STARTED
                case tasks.Progress.IN_PROGRESS:
                    progress = tasks.Progress.IN_PROGRESS
                    break
                case tasks.Progress.COMPLETED:
                    if progress is tasks.Progress.NOT_STARTED:
                        progress = tasks.Progress.IN_PROGRESS
                        break
                    progress = tasks.Progress.COMPLETED

        assert progress
        task_to_progress_map[task] = progress
        return progress

    def are_all_upstream_tasks_completed_recursive(
        task: tasks.UID,
        system: tasks.ISystemView,
        task_to_are_all_upstream_tasks_completed_map: MutableMapping[tasks.UID, bool],
        task_to_progress_map: MutableMapping[tasks.UID, tasks.Progress],
    ) -> bool:
        if task in task_to_are_all_upstream_tasks_completed_map:
            return task_to_are_all_upstream_tasks_completed_map[task]

        are_all_upstream_tasks_completed = all(
            get_progress_recursive(dependee_task, system, task_to_progress_map)
            is tasks.Progress.COMPLETED
            for dependee_task in system.network_graph()
            .dependency_graph()
            .dependee_tasks(task)
        ) and all(
            are_all_upstream_tasks_completed_recursive(
                supertask,
                system,
                task_to_are_all_upstream_tasks_completed_map,
                task_to_progress_map,
            )
            for supertask in system.network_graph().hierarchy_graph().supertasks(task)
        )

        task_to_are_all_upstream_tasks_completed_map[task] = (
            are_all_upstream_tasks_completed
        )
        return are_all_upstream_tasks_completed

    def get_importance_recursive(
        task: tasks.UID,
        system: tasks.ISystemView,
        task_to_importance_map: MutableMapping[tasks.UID, tasks.Importance | None],
    ) -> tasks.Importance | None:
        if system.attributes_register()[task].importance is not None:
            return system.attributes_register()[task].importance

        if task in task_to_importance_map:
            return task_to_importance_map[task]

        importance: tasks.Importance | None = None
        for supertask in system.network_graph().hierarchy_graph().supertasks(task):
            supertask_importance = get_importance_recursive(
                supertask, system, task_to_importance_map
            )
            if supertask_importance is None:
                continue
            if importance is None or supertask_importance > importance:
                importance = supertask_importance
            if importance is tasks.Importance.HIGH:
                break

        task_to_importance_map[task] = importance
        return importance

    def get_highest_downstream_importance_recursive(
        task: tasks.UID,
        system: tasks.ISystemView,
        task_to_highest_downstream_importance_map: MutableMapping[
            tasks.UID, tasks.Importance | None
        ],
        task_to_importance_map: MutableMapping[tasks.UID, tasks.Importance | None],
    ) -> tasks.Importance | None:
        if task in task_to_highest_downstream_importance_map:
            return task_to_highest_downstream_importance_map[task]

        highest_downstream_importance: tasks.Importance | None = None
        for downstream_importance in itertools.chain(
            map(
                functools.partial(
                    get_importance_recursive,
                    system=system,
                    task_to_importance_map=task_to_importance_map,
                ),
                system.network_graph().dependency_graph().dependent_tasks(task),
            ),
            map(
                functools.partial(
                    get_highest_downstream_importance_recursive,
                    system=system,
                    task_to_highest_downstream_importance_map=task_to_highest_downstream_importance_map,
                    task_to_importance_map=task_to_importance_map,
                ),
                itertools.chain(
                    system.network_graph().dependency_graph().dependent_tasks(task),
                    system.network_graph().hierarchy_graph().supertasks(task),
                ),
            ),
        ):
            if downstream_importance is None:
                continue
            if (
                highest_downstream_importance is None
                or downstream_importance > highest_downstream_importance
            ):
                highest_downstream_importance = downstream_importance
            if highest_downstream_importance is tasks.Importance.HIGH:
                break

        task_to_highest_downstream_importance_map[task] = highest_downstream_importance
        return highest_downstream_importance

    task_to_are_all_upstream_tasks_completed_map = dict[tasks.UID, bool]()
    task_to_progress_map = dict[tasks.UID, tasks.Progress]()
    task_to_importance_map = dict[tasks.UID, tasks.Importance | None]()
    task_to_highest_downstream_importance_map = dict[
        tasks.UID, tasks.Importance | None
    ]()

    return [
        (
            task,
            score_card.combined_importance,
            score_card.importance,
            score_card.progress,
        )
        for task, score_card in sorted(
            (
                (
                    task,
                    PriorityScoreCard(
                        get_importance=functools.partial(
                            get_importance_recursive,
                            task=task,
                            system=system.task_system(),
                            task_to_importance_map=task_to_importance_map,
                        ),
                        get_highest_downstream_importance=functools.partial(
                            get_highest_downstream_importance_recursive,
                            task=task,
                            system=system.task_system(),
                            task_to_highest_downstream_importance_map=task_to_highest_downstream_importance_map,
                            task_to_importance_map=task_to_importance_map,
                        ),
                        progress=system.task_system().get_progress(task),
                    ),
                )
                for task in system.task_system()
                .network_graph()
                .hierarchy_graph()
                .concrete_tasks()
                if system.task_system().get_progress(task) is tasks.Progress.IN_PROGRESS
                or (
                    system.task_system().get_progress(task)
                    is tasks.Progress.NOT_STARTED
                    and are_all_upstream_tasks_completed_recursive(
                        task,
                        system.task_system(),
                        task_to_are_all_upstream_tasks_completed_map,
                        task_to_progress_map,
                    )
                )
            ),
            key=lambda x: (x[1], -int(x[0])),
            reverse=True,
        )
    ]
