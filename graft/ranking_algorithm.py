import dataclasses
import datetime
import functools
import operator
from collections.abc import Generator
from typing import AbstractSet, Collection, Iterable, Mapping, Optional, Sequence

from graft.constrained_graph import ConstrainedGraph
from graft.duration import Duration
from graft.priority import Priority
from graft.progress import Progress
from graft.task_attributes import TaskAttributes

# TODO: Change typing to collections.abc
# TODO: Replace most Mapping to MutableMapping


@dataclasses.dataclass
class TaskNetworkAttributes:
    priority: Optional[Priority] = None
    due_datetime: Optional[datetime.datetime] = None
    start_datetime: Optional[datetime.datetime] = None

    @classmethod
    def from_task_attributes(
        cls, task_attributes: TaskAttributes
    ) -> "TaskNetworkAttributes":
        return cls(
            priority=task_attributes.priority,
            due_datetime=task_attributes.due_datetime,
            start_datetime=task_attributes.start_datetime,
        )


@functools.total_ordering
@dataclasses.dataclass
class TaskRankingAttributes:
    priority: Optional[Priority]
    progress: Duration
    duration: Optional[Duration]
    due_datetime: Optional[datetime.datetime]
    start_datetime: Optional[datetime.datetime]

    @classmethod
    def from_attributes(
        cls,
        task_attributes: TaskAttributes,
        task_network_attributes: TaskNetworkAttributes,
    ) -> "TaskRankingAttributes":
        return cls(
            priority=task_network_attributes.priority,
            progress=task_attributes.progress,
            duration=task_attributes.duration,
            due_datetime=task_network_attributes.due_datetime,
            start_datetime=task_network_attributes.start_datetime,
        )

    def __eq__(self, other: "TaskRankingAttributes") -> bool:
        if self.__class__ is not other.__class__:
            raise NotImplementedError

        return (
            self.priority is other.priority
            and self.progress is other.progress
            and self.duration is other.duration
            and self.due_datetime == other.due_datetime
            and self.start_datetime == other.start_datetime
        )

    def __gt__(self, other: "TaskRankingAttributes") -> bool:
        if self.__class__ is not other.__class__:
            raise NotImplementedError

        for metric, equality_operator, comparison_operator in (
            ("priority", operator.is_, operator.gt),
            ("due_datetime", operator.eq, operator.lt),
            ("start_datetime", operator.eq, operator.gt),
            ("duration", operator.is_, operator.lt),
            ("progress", operator.is_, operator.gt),
        ):
            self_metric = getattr(self, metric)
            other_metric = getattr(other, metric)

            if self_metric is None and other_metric is None:
                continue

            if not self_metric:
                return False
            if not other_metric:
                return True

            if equality_operator(self_metric, other_metric):
                continue

            return comparison_operator(self_metric, other_metric)

        return False


def rank_tasks(
    task_attributes_map: Mapping[str, TaskAttributes],
    task_hierarchy: ConstrainedGraph,
    task_dependencies: ConstrainedGraph,
) -> list[str]:

    incomplete_concrete_tasks = list(
        get_incomplete_concrete_tasks(
            task_attributes_map=task_attributes_map,
            task_hierarchy=task_hierarchy,
        )
    )

    incomplete_concrete_task_network_attributes_map = get_task_network_attributes(
        concrete_tasks=incomplete_concrete_tasks,
        task_attributes_map=task_attributes_map,
        task_hierarchy=task_hierarchy,
        task_dependencies=task_dependencies,
    )

    incomplete_concrete_task_ranking_attributes_map = get_task_ranking_attributes(
        concrete_tasks=incomplete_concrete_tasks,
        task_attributes_map=task_attributes_map,
        task_network_attributes_map=incomplete_concrete_task_network_attributes_map,
    )

    ranked_incomplete_concrete_tasks = sorted(
        incomplete_concrete_task_ranking_attributes_map.keys(),
        key=lambda task: incomplete_concrete_task_ranking_attributes_map[task],
    )  # Lowest to highest

    active_concrete_tasks = list(
        get_active_concrete_tasks(
            task_attributes_map=task_attributes_map,
            task_hierarchy=task_hierarchy,
            task_dependencies=task_dependencies,
        )
    )

    startable_active_concrete_tasks = list(
        filter_startable_unblocked_tasks(
            tasks=active_concrete_tasks,
            task_attributes_map=task_attributes_map,
            task_network_attributes_map=incomplete_concrete_task_network_attributes_map,
        )
    )

    ranked_active_concrete_tasks = rank_tasks_against_target_tasks(
        tasks_to_rank=startable_active_concrete_tasks,
        weighted_tasks=ranked_incomplete_concrete_tasks,
        task_attributes_map=task_attributes_map,
        task_network_attributes_map=incomplete_concrete_task_network_attributes_map,
        task_hierarchy=task_hierarchy,
        task_dependencies=task_dependencies,
    )  # Lowest to highest

    return ranked_active_concrete_tasks


def get_incomplete_concrete_tasks(
    task_attributes_map: Mapping[str, TaskAttributes],
    task_hierarchy: ConstrainedGraph,
) -> Generator[str, None, None]:
    for task in task_hierarchy.leaf_nodes():
        if task_attributes_map[task].progress is not Progress.COMPLETED:
            yield task


def get_task_network_attributes(
    concrete_tasks: Collection[str],
    task_attributes_map: Mapping[str, TaskAttributes],
    task_hierarchy: ConstrainedGraph,
    task_dependencies: ConstrainedGraph,
) -> dict[str, TaskNetworkAttributes]:
    """Create a TaskNetworkAttributes object for each concrete task specified."""
    # TODO: Add short circuit if highest possible priority is found
    concrete_task_priority_map = {}
    non_concrete_task_priority_map = {}
    for task in concrete_tasks:
        if task_attributes_map[task].priority:
            priority = task_attributes_map[task].priority
        else:
            priority = get_highest_supertask_priority(
                task=task,
                task_hierarchy=task_hierarchy,
                task_priority_map=non_concrete_task_priority_map,
                task_attributes_map=task_attributes_map,
            )
        concrete_task_priority_map[task] = priority

    concrete_task_due_datetime_map = {}
    task_collection_due_map = {}
    task_above_due_map = {}
    for task in concrete_tasks:
        if task in task_collection_due_map:
            due_datetime = task_collection_due_map[task]
        else:
            due_datetime = get_collection_due(
                task=task,
                task_collection_due_map=task_collection_due_map,
                task_above_due_map=task_above_due_map,
                task_attributes_map=task_attributes_map,
                task_hierarchy=task_hierarchy,
                task_dependencies=task_dependencies,
            )
            task_collection_due_map[task] = due_datetime

        concrete_task_due_datetime_map[task] = due_datetime

    concrete_task_start_datetime_map = {}
    task_collection_start_map = {}
    task_above_start_map = {}
    for task in concrete_tasks:
        if task in task_collection_start_map:
            start_datetime = task_collection_start_map[task]
        else:
            start_datetime = get_collection_start(
                task=task,
                task_collection_start_map=task_collection_start_map,
                task_above_start_map=task_above_start_map,
                task_attributes_map=task_attributes_map,
                task_hierarchy=task_hierarchy,
                task_dependencies=task_dependencies,
            )
            task_collection_start_map[task] = start_datetime

        concrete_task_start_datetime_map[task] = start_datetime

    concrete_task_network_attributes_map = {}
    for task in concrete_tasks:
        highest_priority = concrete_task_priority_map[task]
        earliest_due_datetime = concrete_task_due_datetime_map[task]
        latest_start_datetime = concrete_task_start_datetime_map[task]
        network_attributes = TaskNetworkAttributes(
            priority=highest_priority,
            due_datetime=earliest_due_datetime,
            start_datetime=latest_start_datetime,
        )
        concrete_task_network_attributes_map[task] = network_attributes

    return concrete_task_network_attributes_map


def get_collection_due(
    task: str,
    task_collection_due_map: Mapping[str, Optional[datetime.datetime]],
    task_above_due_map: Mapping[str, Optional[datetime.datetime]],
    task_attributes_map: Mapping[str, TaskAttributes],
    task_hierarchy: ConstrainedGraph,
    task_dependencies: ConstrainedGraph,
) -> Optional[datetime.datetime]:
    """Get latest due datetime of the collected tasks

    collected tasks includes:
    - Above tasks
    - collected tasks of subtasks
    """
    if task in task_above_due_map:
        earliest_due_datetime = task_above_due_map[task]
    else:
        earliest_due_datetime = get_above_due(
            task=task,
            task_collection_due_map=task_collection_due_map,
            task_above_due_map=task_above_due_map,
            task_attributes_map=task_attributes_map,
            task_hierarchy=task_hierarchy,
            task_dependencies=task_dependencies,
        )
        task_above_due_map[task] = earliest_due_datetime

    for subtask in task_hierarchy.successors(node=task):
        if subtask in task_collection_due_map:
            due_datetime = task_collection_due_map[subtask]
        else:
            due_datetime = get_collection_due(
                task=subtask,
                task_collection_due_map=task_collection_due_map,
                task_above_due_map=task_above_due_map,
                task_attributes_map=task_attributes_map,
                task_hierarchy=task_hierarchy,
                task_dependencies=task_dependencies,
            )
            task_collection_due_map[subtask] = due_datetime

        if due_datetime and (
            not earliest_due_datetime or due_datetime < earliest_due_datetime
        ):
            earliest_due_datetime = due_datetime

    return earliest_due_datetime


def get_above_due(
    task: str,
    task_collection_due_map: Mapping[str, Optional[datetime.datetime]],
    task_above_due_map: Mapping[str, Optional[datetime.datetime]],
    task_attributes_map: Mapping[str, TaskAttributes],
    task_hierarchy: ConstrainedGraph,
    task_dependencies: ConstrainedGraph,
) -> Optional[datetime.datetime]:
    """Get earliest due datetime of the above tasks

    above tasks includes:
    - Above tasks
    - Collected tasks of dependents
    """
    earliest_due_datetime = task_attributes_map[task].due_datetime

    for supertask in task_hierarchy.predecessors(node=task):
        if supertask in task_above_due_map:
            due_datetime = task_above_due_map[supertask]
        else:
            due_datetime = get_above_due(
                task=supertask,
                task_collection_due_map=task_collection_due_map,
                task_above_due_map=task_above_due_map,
                task_attributes_map=task_attributes_map,
                task_hierarchy=task_hierarchy,
                task_dependencies=task_dependencies,
            )
            task_above_due_map[supertask] = due_datetime

        if due_datetime and (
            not earliest_due_datetime or due_datetime < earliest_due_datetime
        ):
            earliest_due_datetime = due_datetime

    for dependent in task_dependencies.successors(node=task):
        if dependent in task_collection_due_map:
            due_datetime = task_collection_due_map[dependent]
        else:
            due_datetime = get_collection_due(
                task=dependent,
                task_collection_due_map=task_collection_due_map,
                task_above_due_map=task_above_due_map,
                task_attributes_map=task_attributes_map,
                task_hierarchy=task_hierarchy,
                task_dependencies=task_dependencies,
            )
            task_collection_due_map[dependent] = due_datetime

        if due_datetime and (
            not earliest_due_datetime or due_datetime < earliest_due_datetime
        ):
            earliest_due_datetime = due_datetime

    return earliest_due_datetime


def get_collection_start(
    task: str,
    task_collection_start_map: Mapping[str, Optional[datetime.datetime]],
    task_above_start_map: Mapping[str, Optional[datetime.datetime]],
    task_attributes_map: Mapping[str, TaskAttributes],
    task_hierarchy: ConstrainedGraph,
    task_dependencies: ConstrainedGraph,
) -> Optional[datetime.datetime]:
    """Get latest start datetime of the collected tasks

    collected tasks includes:
    - Above tasks
    - collected tasks of subtasks
    """
    if task in task_above_start_map:
        latest_start_datetime = task_above_start_map[task]
    else:
        latest_start_datetime = get_above_start(
            task=task,
            task_collection_start_map=task_collection_start_map,
            task_above_start_map=task_above_start_map,
            task_attributes_map=task_attributes_map,
            task_hierarchy=task_hierarchy,
            task_dependencies=task_dependencies,
        )
        task_above_start_map[task] = latest_start_datetime

    for subtask in task_hierarchy.successors(node=task):
        if subtask in task_collection_start_map:
            start_datetime = task_collection_start_map[subtask]
        else:
            start_datetime = get_collection_start(
                task=subtask,
                task_collection_start_map=task_collection_start_map,
                task_above_start_map=task_above_start_map,
                task_attributes_map=task_attributes_map,
                task_hierarchy=task_hierarchy,
                task_dependencies=task_dependencies,
            )
            task_collection_start_map[subtask] = start_datetime

        if start_datetime and (
            not latest_start_datetime or start_datetime > latest_start_datetime
        ):
            latest_start_datetime = start_datetime

    return latest_start_datetime


def get_above_start(
    task: str,
    task_collection_start_map: Mapping[str, Optional[datetime.datetime]],
    task_above_start_map: Mapping[str, Optional[datetime.datetime]],
    task_attributes_map: Mapping[str, TaskAttributes],
    task_hierarchy: ConstrainedGraph,
    task_dependencies: ConstrainedGraph,
) -> Optional[datetime.datetime]:
    """Get latest start datetime of the above tasks

    above tasks includes:
    - The current task
    - Above tasks of supertasks
    - Collected tasks of dependees
    """
    latest_start_datetime = task_attributes_map[task].start_datetime

    for supertask in task_hierarchy.predecessors(node=task):
        if supertask in task_above_start_map:
            start_datetime = task_above_start_map[supertask]
        else:
            start_datetime = get_above_start(
                task=supertask,
                task_collection_start_map=task_collection_start_map,
                task_above_start_map=task_above_start_map,
                task_attributes_map=task_attributes_map,
                task_hierarchy=task_hierarchy,
                task_dependencies=task_dependencies,
            )
            task_above_start_map[supertask] = start_datetime

        if start_datetime and (
            not latest_start_datetime or start_datetime > latest_start_datetime
        ):
            latest_start_datetime = start_datetime

    for dependee in task_dependencies.predecessors(node=task):
        if dependee in task_collection_start_map:
            start_datetime = task_collection_start_map[dependee]
        else:
            start_datetime = get_collection_start(
                task=dependee,
                task_collection_start_map=task_collection_start_map,
                task_above_start_map=task_above_start_map,
                task_attributes_map=task_attributes_map,
                task_hierarchy=task_hierarchy,
                task_dependencies=task_dependencies,
            )
            task_collection_start_map[dependee] = start_datetime

        if start_datetime and (
            not latest_start_datetime or start_datetime > latest_start_datetime
        ):
            latest_start_datetime = start_datetime

    return latest_start_datetime


def get_highest_supertask_priority(
    task: str,
    task_hierarchy: ConstrainedGraph,
    task_priority_map: Mapping[str, Optional[Priority]],
    task_attributes_map: Mapping[str, TaskAttributes],
) -> Optional[Priority]:
    """Called if a task has no priority set. Finds the highest priority of its supertasks."""
    highest_supertask_priority = None
    for supertask in task_hierarchy.predecessors(task):
        if task_attributes_map[supertask].priority:
            supertask_priority = task_attributes_map[supertask].priority
        elif supertask in task_priority_map:
            supertask_priority = task_priority_map[supertask]
        else:
            supertask_priority = get_highest_supertask_priority(
                task=supertask,
                task_hierarchy=task_hierarchy,
                task_priority_map=task_priority_map,
                task_attributes_map=task_attributes_map,
            )
            task_priority_map[supertask] = supertask_priority

        if supertask_priority and (
            not highest_supertask_priority
            or supertask_priority > highest_supertask_priority
        ):
            highest_supertask_priority = supertask_priority

    return highest_supertask_priority


def get_task_ranking_attributes(
    concrete_tasks: Iterable[str],
    task_attributes_map: Mapping[str, TaskAttributes],
    task_network_attributes_map: Mapping[str, TaskNetworkAttributes],
) -> dict[str, TaskRankingAttributes]:
    task_ranking_attributes_map = {}
    for task in concrete_tasks:
        task_attributes = task_attributes_map[task]
        task_network_attributes = task_network_attributes_map[task]
        ranking_attributes = TaskRankingAttributes.from_attributes(
            task_attributes=task_attributes,
            task_network_attributes=task_network_attributes,
        )
        task_ranking_attributes_map[task] = ranking_attributes

    return task_ranking_attributes_map


def get_active_concrete_tasks(
    task_attributes_map: Mapping[str, TaskAttributes],
    task_hierarchy: ConstrainedGraph,
    task_dependencies: ConstrainedGraph,
) -> Generator[str, None, None]:
    task_completed_map = {}
    task_forebearers_completed_map = {}

    for task in task_hierarchy.leaf_nodes():
        if task_attributes_map[task].progress is Progress.COMPLETED:
            continue

        if task_attributes_map[task].progress is Progress.IN_PROGRESS:
            yield task
            continue

        # Only concrete tasks remaining are those that have not been started
        if task not in task_forebearers_completed_map:
            are_forebearers_completed = get_task_forebearers_completed(
                task=task,
                task_completed_map=task_completed_map,
                task_forebearers_completed_map=task_forebearers_completed_map,
                task_attributes_map=task_attributes_map,
                task_hierarchy=task_hierarchy,
                task_dependencies=task_dependencies,
            )
            task_forebearers_completed_map[task] = are_forebearers_completed

        if task_forebearers_completed_map[task]:
            yield task


def get_task_forebearers_completed(
    task: str,
    task_completed_map: Mapping[str, bool],
    task_forebearers_completed_map: Mapping[str, bool],
    task_attributes_map: Mapping[str, TaskAttributes],
    task_hierarchy: ConstrainedGraph,
    task_dependencies: ConstrainedGraph,
) -> bool:
    """Task forebearers here refers to:
    - Dependees
    - forebearers of supertasks
    """
    unknown_dependees = []
    for dependee in task_dependencies.predecessors(node=task):
        if (
            task_attributes_map[dependee].progress
            and task_attributes_map[dependee].progress is not Progress.COMPLETED
        ) or (dependee in task_completed_map and not task_completed_map[dependee]):
            return False

        unknown_dependees.append(dependee)

    for dependee in unknown_dependees:
        is_completed = get_non_concrete_task_completed(
            task=dependee,
            task_completed_map=task_completed_map,
            task_attributes_map=task_attributes_map,
            task_hierarchy=task_hierarchy,
        )
        task_completed_map[dependee] = is_completed
        if not is_completed:
            return False

    unknown_supertasks = []
    for supertask in task_hierarchy.predecessors(node=task):
        if (
            supertask in task_forebearers_completed_map
            and not task_forebearers_completed_map[supertask]
        ):
            return False

        unknown_supertasks.append(supertask)

    for supertask in unknown_supertasks:
        are_forebearers_completed = get_task_forebearers_completed(
            task=supertask,
            task_completed_map=task_completed_map,
            task_forebearers_completed_map=task_forebearers_completed_map,
            task_attributes_map=task_attributes_map,
            task_hierarchy=task_hierarchy,
            task_dependencies=task_dependencies,
        )
        task_forebearers_completed_map[supertask] = are_forebearers_completed
        if not are_forebearers_completed:
            return False

    return True


def get_non_concrete_task_completed(
    task: str,
    task_completed_map: Mapping[str, bool],
    task_attributes_map: Mapping[str, TaskAttributes],
    task_hierarchy: ConstrainedGraph,
) -> bool:
    unknown_subtasks = []
    for subtask in task_hierarchy.successors(node=task):
        if (
            task_attributes_map[subtask].progress
            and task_attributes_map[subtask].progress is not Progress.COMPLETED
        ) or (subtask in task_completed_map and not task_completed_map[subtask]):
            return False

        unknown_subtasks.append(subtask)

    for subtask in unknown_subtasks:
        is_completed = get_non_concrete_task_completed(
            task=subtask,
            task_completed_map=task_completed_map,
            task_attributes_map=task_attributes_map,
            task_hierarchy=task_hierarchy,
        )
        task_completed_map[subtask] = is_completed
        if not is_completed:
            return False

    return True


def filter_startable_unblocked_tasks(
    tasks: Iterable[str],
    task_attributes_map: Mapping[str, TaskAttributes],
    task_network_attributes_map: Mapping[str, TaskNetworkAttributes],
) -> Generator[str, None, None]:
    for task in tasks:
        if not task_attributes_map[task].blocked:
            start_datetime = task_network_attributes_map[task].start_datetime
            if not start_datetime or start_datetime <= datetime.datetime.today():
                yield task


def rank_tasks_against_target_tasks(
    tasks_to_rank: Collection[str],
    weighted_tasks: Sequence[str],
    task_attributes_map: Mapping[str, TaskAttributes],
    task_network_attributes_map: Mapping[str, TaskNetworkAttributes],
    task_hierarchy: ConstrainedGraph,
    task_dependencies: ConstrainedGraph,
):
    """
    Rank tasks by the sum of the weighted tasks tasks they are upstream of.

    Use attribute maps to create ranking attributes if paths don't settle the ranking order."""
    # TODO: Can make more efficient by only ranking if task scores need further differentiation; need to go from greatest to least impactful factor
    # TODO: Add attribute ranking on top of upstream ranking
    # Key logic
    # No task to rank will be upstream from another task to rank
    task_upstream_tasks_to_rank_map = {}
    task_upstream_above_tasks_to_rank_map = {}
    task_score_map = {task: 0 for task in tasks_to_rank}
    for weight, task in enumerate(weighted_tasks):
        score = 2**weight
        if task in tasks_to_rank:
            task_score_map[task] += score
            continue

        if task not in task_upstream_tasks_to_rank_map:
            upstream_tasks_to_rank = get_upstream_tasks_to_rank(
                task=task,
                tasks_to_rank=tasks_to_rank,
                task_upstream_tasks_to_rank_map=task_upstream_tasks_to_rank_map,
                task_upstream_above_tasks_to_rank_map=task_upstream_above_tasks_to_rank_map,
                task_hierarchy=task_hierarchy,
                task_dependencies=task_dependencies,
            )
            task_upstream_tasks_to_rank_map[task] = upstream_tasks_to_rank

        for task_to_update in tasks_to_rank:
            task_score_map[task_to_update] += score

    return sorted(tasks_to_rank, key=lambda task: task_score_map[task], reverse=True)


def get_upstream_above_tasks_to_rank(
    task: str,
    tasks_to_rank: Collection[str],
    task_upstream_tasks_to_rank_map: Mapping[str, AbstractSet[str]],
    task_upstream_above_tasks_to_rank_map: Mapping[str, AbstractSet[str]],
    task_hierarchy: ConstrainedGraph,
    task_dependencies: ConstrainedGraph,
) -> frozenset[str]:
    """Here upstream above refers to:
    - dependees
    - upstream of dependees
    - upstream above of supertasks
    """
    upstream_above_tasks_to_rank = set()
    for supertask in task_hierarchy.predecessors(node=task):
        if supertask not in task_upstream_above_tasks_to_rank_map:
            supertask_upstream_above_tasks_to_rank = get_upstream_above_tasks_to_rank(
                task=supertask,
                tasks_to_rank=tasks_to_rank,
                task_upstream_tasks_to_rank_map=task_upstream_tasks_to_rank_map,
                task_upstream_above_tasks_to_rank_map=task_upstream_above_tasks_to_rank_map,
                task_hierarchy=task_hierarchy,
                task_dependencies=task_dependencies,
            )
            task_upstream_above_tasks_to_rank_map[
                supertask
            ] = supertask_upstream_above_tasks_to_rank

        upstream_above_tasks_to_rank.update(
            task_upstream_above_tasks_to_rank_map[supertask]
        )

    for dependee in task_dependencies.predecessors(node=task):
        if dependee in tasks_to_rank:
            upstream_above_tasks_to_rank.add(dependee)
            continue

        if dependee not in task_upstream_tasks_to_rank_map:
            dependee_upstream_tasks_to_rank = get_upstream_tasks_to_rank(
                task=dependee,
                tasks_to_rank=tasks_to_rank,
                task_upstream_tasks_to_rank_map=task_upstream_tasks_to_rank_map,
                task_upstream_above_tasks_to_rank_map=task_upstream_above_tasks_to_rank_map,
                task_hierarchy=task_hierarchy,
                task_dependencies=task_dependencies,
            )
            task_upstream_tasks_to_rank_map[dependee] = dependee_upstream_tasks_to_rank

        upstream_above_tasks_to_rank.update(task_upstream_tasks_to_rank_map[dependee])

    return frozenset(upstream_above_tasks_to_rank)


def get_upstream_tasks_to_rank(
    task: str,
    tasks_to_rank: Collection[str],
    task_upstream_tasks_to_rank_map: Mapping[str, frozenset[str]],
    task_upstream_above_tasks_to_rank_map: Mapping[str, frozenset[str]],
    task_hierarchy: ConstrainedGraph,
    task_dependencies: ConstrainedGraph,
) -> frozenset[str]:
    """Here upstream refers to:
    - upstream above of task
    - subtasks
    - upstream of subtasks"""
    if task not in task_upstream_above_tasks_to_rank_map:
        upstream_above_tasks_to_rank = get_upstream_above_tasks_to_rank(
            task=task,
            tasks_to_rank=tasks_to_rank,
            task_upstream_tasks_to_rank_map=task_upstream_tasks_to_rank_map,
            task_upstream_above_tasks_to_rank_map=task_upstream_above_tasks_to_rank_map,
            task_hierarchy=task_hierarchy,
            task_dependencies=task_dependencies,
        )
        task_upstream_above_tasks_to_rank_map[task] = upstream_above_tasks_to_rank

    upstream_tasks_to_rank = set(task_upstream_above_tasks_to_rank_map[task])

    for dependee in task_dependencies.predecessors(node=task):
        if dependee in tasks_to_rank:
            upstream_tasks_to_rank.add(dependee)
            continue

        if dependee not in task_upstream_tasks_to_rank_map:
            dependee_upstream_tasks_to_rank = get_upstream_tasks_to_rank(
                task=dependee,
                tasks_to_rank=tasks_to_rank,
                task_upstream_tasks_to_rank_map=task_upstream_tasks_to_rank_map,
                task_upstream_above_tasks_to_rank_map=task_upstream_above_tasks_to_rank_map,
                task_hierarchy=task_hierarchy,
                task_dependencies=task_dependencies,
            )
            task_upstream_tasks_to_rank_map[dependee] = dependee_upstream_tasks_to_rank

        upstream_tasks_to_rank.update(task_upstream_tasks_to_rank_map[dependee])

    return frozenset(upstream_tasks_to_rank)
