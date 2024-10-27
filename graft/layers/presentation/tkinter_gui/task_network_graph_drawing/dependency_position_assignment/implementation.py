import collections
import itertools
from collections.abc import Generator

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.dependency_position_assignment.position import (
    DependencyPosition,
)


class PartialDependencyPosition:
    def __init__(self, min_position: int | None, max_position: int | None) -> None:
        self.min_position = min_position
        self.max_position = max_position


def _has_upstream_tasks(task: tasks.UID, graph: tasks.INetworkGraphView) -> bool:
    return next(graph.upstream_tasks(task), None) is not None


def _get_tasks_with_no_upstream_tasks(
    graph: tasks.INetworkGraphView,
) -> Generator[tasks.UID]:
    # None represents that we currently don't know if the task has upstream tasks
    task_has_upstream_tasks: dict[tasks.UID, bool | None] = {
        task: None for task in graph.tasks()
    }

    tasks_to_check = collections.deque(graph.hierarchy_graph().top_level_tasks())

    while tasks_to_check:
        task_to_check = tasks_to_check.popleft()
        if task_has_upstream_tasks[task_to_check] is not None:
            continue

        if graph.dependency_graph().dependee_tasks(task_to_check):
            task_has_upstream_tasks[task_to_check] = True

            tasks_to_check.extend(graph.hierarchy_graph().subtasks(task_to_check))
            continue

        task_to_check_has_supertasks_with_upstream_tasks: bool | None = False
        for supertask in graph.hierarchy_graph().supertasks(task_to_check):
            match task_has_upstream_tasks[supertask]:
                case None:
                    task_to_check_has_supertasks_with_upstream_tasks = None
                case True:
                    task_to_check_has_supertasks_with_upstream_tasks = True
                    break
                case False:
                    ...

        if task_to_check_has_supertasks_with_upstream_tasks is None:
            # Need more info to determine if task has upstream tasks or not
            continue

        task_has_upstream_tasks[
            task_to_check
        ] = task_to_check_has_supertasks_with_upstream_tasks

        tasks_to_check.extend(graph.hierarchy_graph().subtasks(task_to_check))

        if task_to_check_has_supertasks_with_upstream_tasks:
            continue

        yield task_to_check


def _get_immediate_upstream_tasks(
    task: tasks.UID, graph: tasks.INetworkGraphView
) -> Generator[tasks.UID, None, None]:
    """Yield the tasks that are immediately upstream of a task.

    The dependee tasks of a task, as well as the dependee tasks of all superior
    tasks of a task.
    """
    tasks_to_visit = collections.deque([task])
    visited_tasks = set[tasks.UID]()

    # TODO: Check if the same immediately upstream task can be encountered
    # multiple times; I have a hunch it can't
    upstream_tasks_found = set[tasks.UID]()

    while tasks_to_visit:
        task2 = tasks_to_visit.popleft()
        if task2 in visited_tasks:
            continue

        visited_tasks.add(task2)

        for dependee_task in graph.dependency_graph().dependee_tasks(task):
            if dependee_task in upstream_tasks_found:
                continue

            yield dependee_task
            upstream_tasks_found.add(dependee_task)

        tasks_to_visit.extend(graph.hierarchy_graph().supertasks(task2))


def get_dependency_positions_unnamed_method(
    graph: tasks.INetworkGraphView,
) -> dict[tasks.UID, DependencyPosition]:
    """Get the dependency positions of tasks.

    Rules:
    - min position == max(max position of upstream tasks) + 1 AND
                      min(min position of inferior tasks)
    - max position == max(max position of subtasks)
    """
    tasks_with_no_upstream_tasks = set(_get_tasks_with_no_upstream_tasks(graph))

    task_partial_positions = dict[tasks.UID, PartialDependencyPosition]()
    for task in graph.tasks():
        if task in tasks_with_no_upstream_tasks:
            min_position = 0
            max_position = 0 if graph.hierarchy_graph().is_concrete(task) else None
        else:
            min_position = None
            max_position = None

        task_partial_positions[task] = PartialDependencyPosition(
            min_position, max_position
        )

    tasks_with_known_max_position = [
        task
        for task, partial_position in task_partial_positions.items()
        if partial_position.max_position is not None
    ]

    supertasks_of_tasks_with_known_max_position = itertools.chain.from_iterable(
        graph.hierarchy_graph().supertasks(task)
        for task in tasks_with_known_max_position
    )
    tasks_to_check_for_max_position = collections.deque(
        supertasks_of_tasks_with_known_max_position
    )

    dependent_tasks_of_tasks_with_known_max_positions = itertools.chain.from_iterable(
        graph.dependency_graph().dependent_tasks(task)
        for task in tasks_with_known_max_position
    )
    tasks_to_check_for_min_position = collections.deque(
        dependent_tasks_of_tasks_with_known_max_positions
    )

    while tasks_to_check_for_max_position or tasks_to_check_for_max_position:
        while tasks_to_check_for_max_position:
            task_to_check = tasks_to_check_for_max_position.pop()

            if task_partial_positions[task_to_check].max_position is not None:
                continue

            # Assuming that task_to_check is not a concrete_task
            max_position: int | None = None
            for subtask in graph.hierarchy_graph().subtasks(task_to_check):
                subtask_max_position = task_partial_positions[subtask].max_position

                if subtask_max_position is None:
                    break

                max_position = (
                    max(max_position, subtask_max_position)
                    if max_position is not None
                    else subtask_max_position
                )
            else:
                # All the subtasks have known max positions
                assert max_position is not None

                task_partial_positions[task_to_check].max_position = max_position

                for supertask in graph.hierarchy_graph().supertasks(task_to_check):
                    tasks_to_check_for_max_position.append(supertask)

        while tasks_to_check_for_min_position:
            task_to_check = tasks_to_check_for_min_position.pop()

            if task_partial_positions[task_to_check].min_position is not None:
                continue

            max_position: int | None = None
            for upstream_task in _get_immediate_upstream_tasks(task_to_check, graph):
                upstream_task_max_position = task_partial_positions[
                    upstream_task
                ].max_position

                if upstream_task_max_position is None:
                    break

                max_position = (
                    max(max_position, upstream_task_max_position)
                    if max_position is not None
                    else upstream_task_max_position
                )
            else:
                # All the upstream tasks have known max positions
                assert max_position is not None

                task_to_check_min_position = max_position + 1

                task_partial_positions[
                    task_to_check
                ].min_position = task_to_check_min_position

                if graph.hierarchy_graph().is_concrete(task_to_check):
                    task_partial_positions[
                        task_to_check
                    ].max_position = task_to_check_min_position

                for dependent_task in graph.dependency_graph().dependent_tasks(
                    task_to_check
                ):
                    tasks_to_check_for_min_position.append(dependent_task)

    task_positions = dict[tasks.UID, DependencyPosition]()
    for task, partial_position in task_partial_positions.items():
        assert partial_position.min_position is not None
        assert partial_position.max_position is not None

        task_positions[task] = DependencyPosition(
            partial_position.min_position, partial_position.max_position
        )

    return task_positions
