import itertools
import math
from collections.abc import Generator, Iterable, Sequence

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.implementation.depth_graph import (
    get_constrained_depth_graph,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.implementation.depth_indexes.hierarchy_layer import (
    HierarchyLayer,
)


class Hierarchy:
    def __init__(
        self,
        dependency_position: float,
        supertask_depth_index: int,
        subtask_depth_index: int,
    ) -> None:
        self._dependency_position = dependency_position
        self._supertask_index = supertask_depth_index
        self._subtask_index = subtask_depth_index

    @property
    def dependency_position(self) -> float:
        return self._dependency_position

    @property
    def supertask_depth_index(self) -> int:
        return self._supertask_index

    @property
    def subtask_depth_index(self) -> int:
        return self._subtask_index


def _do_hierarchies_intersect(hierarchy1: Hierarchy, hierarchy2: Hierarchy, /) -> bool:
    return math.isclose(
        hierarchy1.dependency_position, hierarchy2.dependency_position
    ) and (
        (
            (hierarchy1.supertask_depth_index < hierarchy2.supertask_depth_index)
            and (hierarchy1.subtask_depth_index > hierarchy2.subtask_depth_index)
        )
        or (
            (hierarchy1.supertask_depth_index > hierarchy2.supertask_depth_index)
            and (hierarchy1.subtask_depth_index < hierarchy2.subtask_depth_index)
        )
    )


def _get_hierarchies(
    supertask_layer: HierarchyLayer,
    subtask_layer: HierarchyLayer,
    graph: tasks.IHierarchyGraphView,
) -> Generator[Hierarchy, None, None]:
    for supertask in supertask_layer.tasks:
        for subtask in graph.subtasks(supertask):
            if subtask not in subtask_layer.tasks:
                continue

            yield Hierarchy(
                dependency_position=subtask_layer.task_to_dependency_midpoint_map[
                    subtask
                ],
                supertask_depth_index=supertask_layer.task_to_depth_index_map[
                    supertask
                ],
                subtask_depth_index=subtask_layer.task_to_depth_index_map[subtask],
            )


def _get_number_of_intersecting_hierarchies_between_layers(
    supertask_layer: HierarchyLayer,
    subtask_layer: HierarchyLayer,
    graph: tasks.IHierarchyGraphView,
) -> int:
    hierarchies = _get_hierarchies(
        supertask_layer=supertask_layer, subtask_layer=subtask_layer, graph=graph
    )
    return sum(
        1
        for hierarchy1, hierarchy2 in itertools.combinations(hierarchies, 2)
        if _do_hierarchies_intersect(hierarchy1, hierarchy2)
    )


def _get_number_of_intersecting_hierarchies_with_adjacent_layers(
    previous_layer: HierarchyLayer | None,
    layer: HierarchyLayer,
    next_layer: HierarchyLayer | None,
    graph: tasks.IHierarchyGraphView,
) -> int:
    number_of_intersecting_hierarchies = 0
    if previous_layer is not None:
        number_of_intersecting_hierarchies += (
            _get_number_of_intersecting_hierarchies_between_layers(
                supertask_layer=previous_layer, subtask_layer=layer, graph=graph
            )
        )
    if next_layer is not None:
        number_of_intersecting_hierarchies += (
            _get_number_of_intersecting_hierarchies_between_layers(
                supertask_layer=layer, subtask_layer=next_layer, graph=graph
            )
        )

    return number_of_intersecting_hierarchies


def _triowise[T](iterable: Iterable[T]) -> Iterable[tuple[T, T, T]]:
    """Like itertools.pairwise, but with 3 elements instead."""
    iterable1, iterable2, iterable3 = itertools.tee(iterable, 3)
    return zip(
        iterable1,
        itertools.islice(iterable2, 1, None),
        itertools.islice(iterable3, 2, None), strict=False,
    )


def transpose(
    graph: tasks.IHierarchyGraphView,
    layers: Sequence[HierarchyLayer],
) -> None:
    is_improved = True
    extended_layers: list[HierarchyLayer | None] = [None, *layers, None]
    while is_improved:
        is_improved = False
        for previous_layer, layer, next_layer in _triowise(extended_layers):
            assert layer is not None
            number_of_hierarchy_intersections = (
                _get_number_of_intersecting_hierarchies_with_adjacent_layers(
                    previous_layer=previous_layer,
                    layer=layer,
                    next_layer=next_layer,
                    graph=graph,
                )
            )

            depth_graph = get_constrained_depth_graph(
                layer.dependency_groups, layer.task_to_depth_index_map
            )
            for shallower_task, deeper_task in list(depth_graph.edges()):
                depth_graph.remove_edge(source=shallower_task, target=deeper_task)

                if (
                    shallower_task == deeper_task
                    or deeper_task in depth_graph.descendants([shallower_task])
                ):
                    # Swapping these two tasks will introduce a cycle, so don't
                    depth_graph.add_edge(source=shallower_task, target=deeper_task)
                    continue

                (
                    layer.task_to_depth_index_map[shallower_task],
                    layer.task_to_depth_index_map[deeper_task],
                ) = (
                    layer.task_to_depth_index_map[deeper_task],
                    layer.task_to_depth_index_map[shallower_task],
                )

                number_of_hierarchy_intersections_with_tasks_transposed = (
                    _get_number_of_intersecting_hierarchies_with_adjacent_layers(
                        previous_layer=previous_layer,
                        layer=layer,
                        next_layer=next_layer,
                        graph=graph,
                    )
                )

                if (
                    number_of_hierarchy_intersections_with_tasks_transposed
                    >= number_of_hierarchy_intersections
                ):
                    # Swap everything back
                    depth_graph.add_edge(source=shallower_task, target=deeper_task)
                    (
                        layer.task_to_depth_index_map[shallower_task],
                        layer.task_to_depth_index_map[deeper_task],
                    ) = (
                        layer.task_to_depth_index_map[deeper_task],
                        layer.task_to_depth_index_map[shallower_task],
                    )
                    continue

                number_of_hierarchy_intersections = (
                    number_of_hierarchy_intersections_with_tasks_transposed
                )
                depth_graph.add_edge(source=deeper_task, target=shallower_task)
                is_improved = True
