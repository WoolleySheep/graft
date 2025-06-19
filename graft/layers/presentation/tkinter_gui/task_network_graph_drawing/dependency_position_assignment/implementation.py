import itertools
from collections.abc import Generator, MutableMapping

from graft import graphs
from graft.domain import tasks
from graft.domain.tasks.network_graph import INetworkGraphView
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.dependency_position_assignment.position import (
    DependencyLayers,
)


class PartialDependencyPosition:
    def __init__(self, min_: int | None, max_: int | None) -> None:
        self.min = min_
        self.max = max_

    def __str__(self) -> str:
        return f"{{min{self.min}, max={self.max}}}"

    def __repr__(self) -> str:
        return f"{__class__.__name__}(min={self.min}, max={self.max})"


def _get_tasks_with_no_upstream_tasks(
    graph: tasks.INetworkGraphView,
) -> Generator[tasks.UID]:
    # None represents that we currently don't know if the task has upstream tasks
    task_has_upstream_tasks: dict[tasks.UID, bool | None] = dict.fromkeys(graph.tasks())

    tasks_to_check = list(graph.hierarchy_graph().top_level_tasks())

    while tasks_to_check:
        task_to_check = tasks_to_check.pop()
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

        task_has_upstream_tasks[task_to_check] = (
            task_to_check_has_supertasks_with_upstream_tasks
        )

        tasks_to_check.extend(graph.hierarchy_graph().subtasks(task_to_check))

        if task_to_check_has_supertasks_with_upstream_tasks:
            continue

        yield task_to_check


def _get_immediate_upstream_tasks(
    task: tasks.UID,
    graph: INetworkGraphView,
    task_to_immediate_upstream_tasks_map: MutableMapping[tasks.UID, set[tasks.UID]],
) -> set[tasks.UID]:
    if task in task_to_immediate_upstream_tasks_map:
        return task_to_immediate_upstream_tasks_map[task]

    immediate_upstream_tasks = set[tasks.UID](
        graph.dependency_graph().dependee_tasks(task)
    )
    for supertask in graph.hierarchy_graph().supertasks(task):
        supertask_immediate_upstream_tasks = _get_immediate_upstream_tasks(
            supertask, graph, task_to_immediate_upstream_tasks_map
        )
        immediate_upstream_tasks.update(supertask_immediate_upstream_tasks)

    task_to_immediate_upstream_tasks_map[task] = immediate_upstream_tasks
    return immediate_upstream_tasks


def _generate_min_position_dependency_mapping(
    graph: INetworkGraphView,
) -> graphs.BiDirectionalSetDict[tasks.UID]:
    task_to_concrete_min_position_dependents_map = graphs.BiDirectionalSetDict[
        tasks.UID
    ]()

    task_to_immediate_upstream_tasks_map = dict[tasks.UID, set[tasks.UID]]()
    for task in graph.tasks():
        task_to_concrete_min_position_dependents_map.add(task, None)

        if graph.hierarchy_graph().is_concrete(task):
            for min_position_dependee in _get_immediate_upstream_tasks(
                task=task,
                graph=graph,
                task_to_immediate_upstream_tasks_map=task_to_immediate_upstream_tasks_map,
            ):
                task_to_concrete_min_position_dependents_map.add(
                    min_position_dependee, task
                )

    return task_to_concrete_min_position_dependents_map


def get_dependency_positions_unnamed_method(
    graph: tasks.INetworkGraphView,
) -> dict[tasks.UID, DependencyLayers]:
    """Get the dependency positions of tasks.

    Rules:
    - min position (concrete tasks) == max(max position of upstream tasks) + 1
    - min position (non-concrete tasks) == min(min position of inferior tasks)
    - max position (concrete tasks) == min position
    - max position (non-concrete tasks)== max(max position of inferior tasks)
    """
    task_to_concrete_min_position_dependents_map = (
        _generate_min_position_dependency_mapping(graph)
    )

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
        if partial_position.max is not None
    ]

    tasks_to_check_for_max_position = list(
        itertools.chain.from_iterable(
            graph.hierarchy_graph().supertasks(task)
            for task in tasks_with_known_max_position
        )
    )

    concrete_tasks_to_check_for_min_position = list(
        itertools.chain.from_iterable(
            task_to_concrete_min_position_dependents_map[task]
            for task in tasks_with_known_max_position
        )
    )

    tasks_with_known_min_position = (
        task
        for task, partial_position in task_partial_positions.items()
        if partial_position.min is not None
    )

    non_concrete_tasks_to_check_for_min_position = list(
        itertools.chain.from_iterable(
            graph.hierarchy_graph().supertasks(task)
            for task in tasks_with_known_min_position
        )
    )

    while (
        tasks_to_check_for_max_position
        or concrete_tasks_to_check_for_min_position
        or non_concrete_tasks_to_check_for_min_position
    ):
        while tasks_to_check_for_max_position:
            task_to_check = tasks_to_check_for_max_position.pop()

            if task_partial_positions[task_to_check].max is not None:
                continue

            # Assuming that the task we're checking is not a concrete_task
            max_position: int | None = None
            for subtask in graph.hierarchy_graph().subtasks(task_to_check):
                subtask_max_position = task_partial_positions[subtask].max

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

                task_partial_positions[task_to_check].max = max_position

                tasks_to_check_for_max_position.extend(
                    graph.hierarchy_graph().supertasks(task_to_check)
                )

                concrete_tasks_to_check_for_min_position.extend(
                    task_to_concrete_min_position_dependents_map[task_to_check]
                )

        while concrete_tasks_to_check_for_min_position:
            task_to_check = concrete_tasks_to_check_for_min_position.pop()

            if task_partial_positions[task_to_check].min is not None:
                continue

            upstream_dependents_max_position: int | None = None
            for (
                upstream_dependent_task
            ) in task_to_concrete_min_position_dependents_map.inverse[task_to_check]:
                upstream_dependent_max_position = task_partial_positions[
                    upstream_dependent_task
                ].max

                if upstream_dependent_max_position is None:
                    break

                upstream_dependents_max_position = (
                    max(
                        upstream_dependents_max_position,
                        upstream_dependent_max_position,
                    )
                    if upstream_dependents_max_position is not None
                    else upstream_dependent_max_position
                )
            else:
                # All the upstream dependents have known max positions
                assert upstream_dependents_max_position is not None

                concrete_task_position = upstream_dependents_max_position + 1

                task_partial_positions[task_to_check].min = concrete_task_position
                non_concrete_tasks_to_check_for_min_position.extend(
                    graph.hierarchy_graph().supertasks(task_to_check)
                )

                task_partial_positions[task_to_check].max = concrete_task_position
                concrete_tasks_to_check_for_min_position.extend(
                    task_to_concrete_min_position_dependents_map[task_to_check]
                )
                tasks_to_check_for_max_position.extend(
                    graph.hierarchy_graph().supertasks(task_to_check)
                )

        while non_concrete_tasks_to_check_for_min_position:
            task_to_check = non_concrete_tasks_to_check_for_min_position.pop()

            if task_partial_positions[task_to_check].min is not None:
                continue

            min_position: int | None = None
            for subtask in graph.hierarchy_graph().subtasks(task_to_check):
                subtask_min_position = task_partial_positions[subtask].min

                if subtask_min_position is None:
                    break

                min_position = (
                    min(min_position, subtask_min_position)
                    if min_position is not None
                    else subtask_min_position
                )
            else:
                # All the subtasks have known min positions
                assert min_position is not None

                task_partial_positions[task_to_check].min = min_position
                non_concrete_tasks_to_check_for_min_position.extend(
                    graph.hierarchy_graph().supertasks(task_to_check)
                )

    task_positions = dict[tasks.UID, DependencyLayers]()
    for upstream_dependent_task, partial_position in task_partial_positions.items():
        assert partial_position.min is not None
        assert partial_position.max is not None

        task_positions[upstream_dependent_task] = DependencyLayers(
            partial_position.min, partial_position.max
        )

    return task_positions
