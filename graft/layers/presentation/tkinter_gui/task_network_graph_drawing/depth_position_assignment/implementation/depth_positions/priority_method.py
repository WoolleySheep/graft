import itertools
from collections.abc import (
    Mapping,
    MutableMapping,
)
from typing import Final

from graft import graphs
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.dependency_axis_grouping import (
    get_dependency_axis_groups,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.implementation.depth_graph import (
    get_constrained_depth_graph,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.implementation.dummy_tasks import (
    DummyUID,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.task_layers import (
    TaskRelationLayers,
    get_hierarchy_layers_in_descending_order,
)

NUMBER_OF_DEPTH_POSITION_ITERATIONS: Final = 15

# TODO: Change implementation to, instead of using dependency-linked tasks as weights,
# to add a step explicitly sweeping along the dependency axis in both directions.
# This may have its own shortcomings. The current approach is good enough for now, so no
# rush.


class Priority:
    """Priority of a task for movement purposes.

    Having no priority set is the highest priority of all.
    """

    def __init__(self, n: int | None = None) -> None:
        self.n = n

    def __bool__(self) -> bool:
        return self.n is None or bool(self.n)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Priority) and self.n == other.n

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Priority):
            raise NotImplementedError

        return self.n is not None and (other.n is None or self.n < other.n)

    def __str__(self) -> str:
        return f"Priority({self.n})"

    def __repr__(self) -> str:
        return str(self)


def _get_weighted_average_depth_position_of_supertasks_and_dependency_linked_tasks(
    task: tasks.UID,
    graph: tasks.INetworkGraphView,
    supertask_to_depth_position_map: Mapping[tasks.UID, float],
    dependency_linked_task_to_depth_position_map: Mapping[tasks.UID, float],
) -> float:
    return (
        2
        * (
            sum(
                supertask_to_depth_position_map[task_]
                for task_ in graph.hierarchy_graph().supertasks(task)
            )
        )
        + sum(
            dependency_linked_task_to_depth_position_map[task_]
            for task_ in itertools.chain(
                graph.dependency_graph().dependee_tasks(task),
                graph.dependency_graph().dependent_tasks(task),
            )
        )
    ) / (
        2 * len(graph.hierarchy_graph().supertasks(task))
        + len(graph.dependency_graph().dependee_tasks(task))
        + len(graph.dependency_graph().dependent_tasks(task))
    )


def _get_weighted_average_depth_position_of_subtasks_and_dependency_linked_tasks(
    task: tasks.UID,
    graph: tasks.INetworkGraphView,
    subtask_to_depth_position_map: Mapping[tasks.UID, float],
    dependency_linked_task_to_depth_position_map: Mapping[tasks.UID, float],
) -> float:
    return (
        2
        * (
            sum(
                subtask_to_depth_position_map[task_]
                for task_ in graph.hierarchy_graph().subtasks(task)
            )
        )
        + sum(
            dependency_linked_task_to_depth_position_map[task_]
            for task_ in itertools.chain(
                graph.dependency_graph().dependee_tasks(task),
                graph.dependency_graph().dependent_tasks(task),
            )
        )
    ) / (
        2 * len(graph.hierarchy_graph().subtasks(task))
        + len(graph.dependency_graph().dependee_tasks(task))
        + len(graph.dependency_graph().dependent_tasks(task))
    )


def _move_task(
    task: tasks.UID,
    ideal_position: float,
    layer_depth_graph: graphs.DirectedAcyclicGraph[tasks.UID],
    task_to_depth_position_map: MutableMapping[tasks.UID, float],
    task_to_priority_map: Mapping[tasks.UID, Priority],
    min_separation_distance: float,
) -> None:
    current_position = task_to_depth_position_map[task]

    if current_position < ideal_position:
        _shift_task_deeper(
            task=task,
            threshold_position=ideal_position,
            layer_depth_graph=layer_depth_graph,
            task_to_depth_position_map=task_to_depth_position_map,
            task_to_priority_map=task_to_priority_map,
            min_separation_distance=min_separation_distance,
        )
    elif current_position > ideal_position:
        _shift_task_shallower(
            task=task,
            threshold_position=ideal_position,
            layer_depth_graph=layer_depth_graph,
            task_to_depth_position_map=task_to_depth_position_map,
            task_to_priority_map=task_to_priority_map,
            min_separation_distance=min_separation_distance,
        )


def _shift_task_deeper(
    task: tasks.UID,
    threshold_position: float,
    layer_depth_graph: graphs.DirectedAcyclicGraph[tasks.UID],
    task_to_depth_position_map: MutableMapping[tasks.UID, float],
    task_to_priority_map: Mapping[tasks.UID, Priority],
    min_separation_distance: float,
) -> None:
    # Task is the deepest task - base case
    if layer_depth_graph.is_leaf(task):
        task_to_depth_position_map[task] = max(
            task_to_depth_position_map[task], threshold_position
        )
        return

    for deeper_task in layer_depth_graph.successors(task):
        if task_to_priority_map[deeper_task] < task_to_priority_map[task]:
            _shift_task_deeper(
                task=deeper_task,
                threshold_position=threshold_position + min_separation_distance,
                layer_depth_graph=layer_depth_graph,
                task_to_depth_position_map=task_to_depth_position_map,
                task_to_priority_map=task_to_priority_map,
                min_separation_distance=min_separation_distance,
            )

    deeper_task_positions = (
        task_to_depth_position_map[deeper_task]
        for deeper_task in layer_depth_graph.successors(task)
    )
    task_to_depth_position_map[task] = min(
        itertools.chain(
            [threshold_position],
            (
                deeper_task_position - min_separation_distance
                for deeper_task_position in deeper_task_positions
            ),
        )
    )


def _shift_task_shallower(
    task: tasks.UID,
    threshold_position: float,
    layer_depth_graph: graphs.DirectedAcyclicGraph[tasks.UID],
    task_to_depth_position_map: MutableMapping[tasks.UID, float],
    task_to_priority_map: Mapping[tasks.UID, Priority],
    min_separation_distance: float,
) -> None:
    # Task is the shallowest task - base case
    if layer_depth_graph.is_root(task):
        task_to_depth_position_map[task] = min(
            task_to_depth_position_map[task], threshold_position
        )
        return

    for shallower_task in layer_depth_graph.predecessors(task):
        if task_to_priority_map[shallower_task] < task_to_priority_map[task]:
            _shift_task_shallower(
                task=shallower_task,
                threshold_position=threshold_position - min_separation_distance,
                layer_depth_graph=layer_depth_graph,
                task_to_depth_position_map=task_to_depth_position_map,
                task_to_priority_map=task_to_priority_map,
                min_separation_distance=min_separation_distance,
            )

    shallower_task_positions = (
        task_to_depth_position_map[shallower_task]
        for shallower_task in layer_depth_graph.predecessors(task)
    )
    task_to_depth_position_map[task] = max(
        itertools.chain(
            [threshold_position],
            (
                shallower_task_position + min_separation_distance
                for shallower_task_position in shallower_task_positions
            ),
        )
    )


class HierarchyLayer:
    def __init__(
        self,
        depth_graph: graphs.DirectedAcyclicGraph[tasks.UID],
        task_to_supertask_and_dependency_linked_task_priority_map: Mapping[
            tasks.UID, Priority
        ],
        task_to_subtask_and_dependency_linked_task_priority_map: Mapping[
            tasks.UID, Priority
        ],
    ) -> None:
        self._depth_graph = depth_graph
        self._task_to_supertask_and_dependency_linked_tasks_priority_map = (
            task_to_supertask_and_dependency_linked_task_priority_map
        )
        self._task_to_subtask_and_dependency_linked_task_priority_map = (
            task_to_subtask_and_dependency_linked_task_priority_map
        )
        self._tasks_with_supertasks_or_dependency_linked_tasks_sorted_by_descending_priority = sorted(
            filter(
                lambda task: bool(
                    task_to_supertask_and_dependency_linked_task_priority_map[task]
                ),
                task_to_supertask_and_dependency_linked_task_priority_map.keys(),
            ),
            key=lambda task: task_to_supertask_and_dependency_linked_task_priority_map[
                task
            ],
            reverse=True,
        )
        self._tasks_with_subtasks_or_dependency_linked_tasks_sorted_by_descending_priority = sorted(
            filter(
                lambda task: bool(
                    task_to_subtask_and_dependency_linked_task_priority_map[task]
                ),
                task_to_subtask_and_dependency_linked_task_priority_map.keys(),
            ),
            key=lambda task: task_to_subtask_and_dependency_linked_task_priority_map[
                task
            ],
            reverse=True,
        )

    @property
    def depth_graph(self) -> graphs.DirectedAcyclicGraph[tasks.UID]:
        return self._depth_graph

    @property
    def task_to_supertask_and_dependency_linked_tasks_priority_map(
        self,
    ) -> Mapping[tasks.UID, Priority]:
        return self._task_to_supertask_and_dependency_linked_tasks_priority_map

    @property
    def task_to_subtask_and_dependency_linked_tasks_priority_map(
        self,
    ) -> Mapping[tasks.UID, Priority]:
        return self._task_to_subtask_and_dependency_linked_task_priority_map

    @property
    def tasks_with_supertasks_or_dependencies_sorted_by_descending_priority(
        self,
    ) -> list[tasks.UID]:
        return self._tasks_with_supertasks_or_dependency_linked_tasks_sorted_by_descending_priority

    @property
    def tasks_with_subtasks_or_dependency_linked_tasks_sorted_by_descending_priority(
        self,
    ) -> list[tasks.UID]:
        return self._tasks_with_subtasks_or_dependency_linked_tasks_sorted_by_descending_priority

    def __str__(self) -> str:
        return str(
            str(self._task_to_supertask_and_dependency_linked_tasks_priority_map.keys())
        )

    def __repr__(self) -> str:
        return f"HierarchyLayer{self}"


def get_depth_positions_priority_method(
    graph: tasks.INetworkGraphView,
    task_to_relation_layers_map: Mapping[tasks.UID, TaskRelationLayers],
    task_to_depth_index_map: Mapping[tasks.UID, int],
    starting_separation_distance: float,
    min_separation_distance: float,
) -> dict[tasks.UID, float]:
    if starting_separation_distance <= 0:
        raise ValueError

    if min_separation_distance <= 0:
        raise ValueError

    hierarchy_layers = [
        HierarchyLayer(
            depth_graph=get_constrained_depth_graph(
                get_dependency_axis_groups(
                    tasks_=layer,
                    task_to_relation_layers_map=task_to_relation_layers_map,
                ),
                task_to_depth_index_map,
            ),
            task_to_supertask_and_dependency_linked_task_priority_map={
                task: Priority(
                    None
                    if isinstance(task, DummyUID)
                    else 2 * len(graph.hierarchy_graph().supertasks(task))
                    + len(graph.dependency_graph().dependee_tasks(task))
                    + len(graph.dependency_graph().dependent_tasks(task))
                )
                for task in layer
            },
            task_to_subtask_and_dependency_linked_task_priority_map={
                task: Priority(
                    None
                    if isinstance(task, DummyUID)
                    else 2 * len(graph.hierarchy_graph().subtasks(task))
                    + len(graph.dependency_graph().dependee_tasks(task))
                    + len(graph.dependency_graph().dependent_tasks(task))
                )
                for task in layer
            },
        )
        for layer in get_hierarchy_layers_in_descending_order(
            task_to_relation_layers_map
        )
    ]

    # Populate initial depth positions
    task_to_depth_position_map = {
        task: starting_separation_distance * depth_index
        for task, depth_index in task_to_depth_index_map.items()
    }

    for _ in range(NUMBER_OF_DEPTH_POSITION_ITERATIONS):
        if len(hierarchy_layers) == 1:
            layer = hierarchy_layers[0]
            # Dependency-linked tasks can be in the same layer
            # To avoid weirdness, use the old dependency-linked task positions
            task_to_depth_position_map_copy = task_to_depth_position_map.copy()
            for task in layer.tasks_with_supertasks_or_dependencies_sorted_by_descending_priority:
                # Won't be any supertasks here, only care about the dependencies
                ideal_position = _get_weighted_average_depth_position_of_supertasks_and_dependency_linked_tasks(
                    task=task,
                    graph=graph,
                    supertask_to_depth_position_map=task_to_depth_position_map,
                    dependency_linked_task_to_depth_position_map=task_to_depth_position_map_copy,
                )
                _move_task(
                    task=task,
                    ideal_position=ideal_position,
                    layer_depth_graph=layer.depth_graph,
                    task_to_depth_position_map=task_to_depth_position_map,
                    task_to_priority_map=layer.task_to_supertask_and_dependency_linked_tasks_priority_map,
                    min_separation_distance=min_separation_distance,
                )
            continue

        # Dependency-linked tasks can be in the same layer
        # To avoid weirdness, use the old dependency-linked task positions each
        # iteration and update it for the next
        task_to_depth_position_map_copy = task_to_depth_position_map.copy()

        for layer in itertools.islice(reversed(hierarchy_layers), 1, None):
            for task in layer.tasks_with_subtasks_or_dependency_linked_tasks_sorted_by_descending_priority:
                ideal_position = _get_weighted_average_depth_position_of_subtasks_and_dependency_linked_tasks(
                    task=task,
                    graph=graph,
                    subtask_to_depth_position_map=task_to_depth_position_map,
                    dependency_linked_task_to_depth_position_map=task_to_depth_position_map_copy,
                )
                _move_task(
                    task=task,
                    ideal_position=ideal_position,
                    layer_depth_graph=layer.depth_graph,
                    task_to_depth_position_map=task_to_depth_position_map,
                    task_to_priority_map=layer.task_to_subtask_and_dependency_linked_tasks_priority_map,
                    min_separation_distance=min_separation_distance,
                )

        for layer in itertools.islice(hierarchy_layers, 1, None):
            for task in layer.tasks_with_supertasks_or_dependencies_sorted_by_descending_priority:
                ideal_position = _get_weighted_average_depth_position_of_supertasks_and_dependency_linked_tasks(
                    task=task,
                    graph=graph,
                    supertask_to_depth_position_map=task_to_depth_position_map,
                    dependency_linked_task_to_depth_position_map=task_to_depth_position_map_copy,
                )
                _move_task(
                    task=task,
                    ideal_position=ideal_position,
                    layer_depth_graph=layer.depth_graph,
                    task_to_depth_position_map=task_to_depth_position_map,
                    task_to_priority_map=layer.task_to_supertask_and_dependency_linked_tasks_priority_map,
                    min_separation_distance=min_separation_distance,
                )

    return task_to_depth_position_map
