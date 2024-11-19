import itertools
import math
from collections.abc import Callable, Generator, Iterable, Mapping, MutableMapping
from typing import Protocol

from graft.domain import tasks
from graft.domain.tasks.network_graph import NetworkGraph
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.dependency_position_assignment import (
    DependencyLayers,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.task_layers import (
    TaskRelationLayers,
)


class DummyUID(tasks.UID):
    """UID of task introduced to ensure single-level hierarchies."""

    def __eq__(self, other: object) -> bool:
        """Check if dummy UID is equal to other."""
        return isinstance(other, DummyUID) and int(self) == int(other)

    def __hash__(self) -> int:
        """Return hash of the UID number.

        Needs to be overridden explicitly as hash function defaults to None when
        equality dunder is overridden in subclass.
        """
        return super().__hash__()

    def __lt__(self, other: object) -> bool:
        """Check if dummy UID is less than other."""
        return isinstance(other, DummyUID) and int(self) < int(other)

    def __repr__(self) -> str:
        """Return string representation of dummy UID."""
        return f"dummy_uid({self._number!r})"


def _closest_element[T: float](
    iterable_ordered_by_ascending: Iterable[T], value: T
) -> T:
    """Return the element in the iterable with the minimum absolute difference to value.

    The iterable must be ordered by ascending order.
    """
    min_difference = float("inf")
    closest_element: T | None = None

    for element in iterable_ordered_by_ascending:
        difference = abs(element - value)

        if difference < min_difference:
            min_difference = difference
            closest_element = element

        # Once the elements are larger than the value, they're only going to
        # keep getting further away. Stop searching
        if element >= value:
            break

    if closest_element is None:
        raise ValueError

    return closest_element


def _within_range(
    sorted_iterable: Iterable[int], lower_bound: int, upper_bound: int
) -> Generator[int, None, None]:
    """Yield all items in sorted iterable that are within the given range.

    Note that it is < and >, not <= and >=.
    """
    if lower_bound >= upper_bound:
        raise ValueError

    for item in itertools.dropwhile(
        lambda value: value <= lower_bound, sorted_iterable
    ):
        if item >= upper_bound:
            break
        yield item


def _get_unique_dummy_uid_factory() -> Callable[[], DummyUID]:
    """Create a function that, every time it is called, produces a unique Dummy UID.

    UID's will only be unique when compared to UID's produced by the same function.
    """
    counter = 0

    def get_unique_dummy_uid() -> DummyUID:
        nonlocal counter
        task = DummyUID(counter)
        counter += 1
        return task

    return get_unique_dummy_uid


def _scale_dependency_position(
    position: DependencyLayers,
) -> DependencyLayers:
    """Stretch out the position of true task along the dependency axis.

    This is done because dependency dummy tasks can exist at 0.5 increments; by
    stretching dependency positions out by a factor of 2, we can keep these as
    integers.
    """
    return DependencyLayers(2 * position.min, 2 * position.max)


def _get_tasks_scaled_on_dependency_axis(
    task_to_relation_layers_map: Mapping[tasks.UID, TaskRelationLayers],
) -> dict[tasks.UID, TaskRelationLayers]:
    return {
        task: TaskRelationLayers(
            dependency_layers=_scale_dependency_position(position.dependency),
            hierarchy_layer=position.hierarchy,
        )
        for task, position in task_to_relation_layers_map.items()
    }


def _replace_multilevel_hierarchies_with_single_level_dummies(
    get_unique_dummy_task: Callable[[], DummyUID],
    graph: NetworkGraph,
    task_to_relation_layers_map: MutableMapping[tasks.UID, TaskRelationLayers],
) -> None:
    sorted_hierarchy_layers = sorted(
        {layers.hierarchy for layers in task_to_relation_layers_map.values()}
    )

    for supertask, subtask in list(graph.hierarchy_graph().hierarchies()):
        subtask_dependency_midpoint = (
            task_to_relation_layers_map[subtask].dependency.min
            + task_to_relation_layers_map[subtask].dependency.max
        ) / 2

        # Assuming that tasks have already been scaled at this point, so the
        # midpoint should be at a whole number
        assert math.isclose(subtask_dependency_midpoint % 1, 0)
        subtask_dependency_midpoint_rounded = round(subtask_dependency_midpoint)
        dummy_dependency_layers = DependencyLayers(
            subtask_dependency_midpoint_rounded, subtask_dependency_midpoint_rounded
        )
        dummy_tasks_replacing_current_hierarchy = list[DummyUID]()
        for hierarchy_layer in _within_range(
            sorted_hierarchy_layers,
            task_to_relation_layers_map[subtask].hierarchy,
            task_to_relation_layers_map[supertask].hierarchy,
        ):
            dummy_task = get_unique_dummy_task()
            dummy_tasks_replacing_current_hierarchy.append(dummy_task)
            graph.add_task(dummy_task)

            task_to_relation_layers_map[dummy_task] = TaskRelationLayers(
                dependency_layers=dummy_dependency_layers,
                hierarchy_layer=hierarchy_layer,
            )

        if not dummy_tasks_replacing_current_hierarchy:
            continue

        graph.remove_hierarchy(supertask, subtask)

        tasks_in_hierarchy_chain = itertools.chain(
            [subtask], dummy_tasks_replacing_current_hierarchy, [supertask]
        )

        for dummy_subtask, dummy_supertask in itertools.pairwise(
            tasks_in_hierarchy_chain
        ):
            graph.add_hierarchy(dummy_supertask, dummy_subtask)


def _replace_multilevel_dependencies_with_single_level_dummies(
    get_unique_dummy_task: Callable[[], DummyUID],
    graph: NetworkGraph,
    task_to_relation_layers_map: MutableMapping[tasks.UID, TaskRelationLayers],
) -> None:
    sorted_dependency_levels = sorted(
        {layers.dependency.min for layers in task_to_relation_layers_map.values()}
    )

    sorted_hierarchy_levels = sorted(
        {layers.hierarchy for layers in task_to_relation_layers_map.values()}
    )

    for dependee_task, dependent_task in list(graph.dependency_graph().dependencies()):
        hierarchy_change_gradient = (
            task_to_relation_layers_map[dependent_task].hierarchy
            - task_to_relation_layers_map[dependee_task].hierarchy
        ) / (
            task_to_relation_layers_map[dependent_task].dependency.min
            - task_to_relation_layers_map[dependee_task].dependency.max
        )

        dummy_tasks_replacing_current_dependency = list[DummyUID]()
        for dependency_level in _within_range(
            sorted_dependency_levels,
            task_to_relation_layers_map[dependee_task].dependency.max,
            task_to_relation_layers_map[dependent_task].dependency.min,
        ):
            dummy_task = get_unique_dummy_task()
            dummy_tasks_replacing_current_dependency.append(dummy_task)
            graph.add_task(dummy_task)

            # Get the closest hierarchy level to the interpolated hierarchy level
            dependency_level_delta = (
                dependency_level
                - task_to_relation_layers_map[dependee_task].dependency.max
            )
            interpolated_hierarchy_level = (
                hierarchy_change_gradient * dependency_level_delta
                + task_to_relation_layers_map[dependee_task].hierarchy
            )

            closest_hierarchy_level = round(
                _closest_element(sorted_hierarchy_levels, interpolated_hierarchy_level)
            )

            task_to_relation_layers_map[dummy_task] = TaskRelationLayers(
                dependency_layers=DependencyLayers(dependency_level, dependency_level),
                hierarchy_layer=closest_hierarchy_level,
            )

        if not dummy_tasks_replacing_current_dependency:
            continue

        graph.remove_dependency(dependee_task, dependent_task)

        tasks_in_dependency_chain = itertools.chain(
            [dependee_task], dummy_tasks_replacing_current_dependency, [dependent_task]
        )
        for dummy_dependee_task, dummy_dependent_task in itertools.pairwise(
            tasks_in_dependency_chain
        ):
            graph.add_dependency(dummy_dependee_task, dummy_dependent_task)


def generate_graph_with_dummy_tasks(
    graph: tasks.INetworkGraphView,
    task_to_relation_layers_map: Mapping[tasks.UID, TaskRelationLayers],
) -> tuple[tasks.NetworkGraph, dict[tasks.UID | DummyUID, TaskRelationLayers]]:
    """Create a clone of the graph with dummy tasks.

    Dummy tasks are added to ensure that a hierarchy only stretches across one
    vertical level; hierarchies that stretched across multiple levels are broken
    into a number of smaller hierarchies, with dummy tasks on the intervening
    levels.

    Hierarchy-replacement dummy tasks have a dependency min/max level equivalent
    to the midpoint of the subtask whose hierarchy they're modifying. This means
    that they can have dependency positions at multiples of 0.5, as opposed to
    the multiples of 1 (aka: integers) allowed for normal task dependency
    positions.

    Dummy tasks are also added to ensure that a dependency only stretches across
    one horizontal level; dependencies that stretched across multiple levels are
    broken into a number of smaller dependencies, with dummy tasks on the
    intervening levels.

    Dependency dummy tasks have a hierarchy level and dependency min/max levels
    interpolated between the dependee and dependent tasks. This is to ensure
    that a dummy task can be found at each dependency level between the dependee
    & dependent.

    My current dummy UID implementation isn't particularly type safe, and
    requires on nobody using the DummyUID class outside this context. Find a
    better way.
    """
    get_unique_dummy_task = _get_unique_dummy_uid_factory()

    graph_with_dummies = tasks.NetworkGraph.clone(graph)

    task_or_dummy_to_scaled_relation_layers_map: dict[
        tasks.UID | DummyUID, TaskRelationLayers
    ] = _get_tasks_scaled_on_dependency_axis(
        task_to_relation_layers_map=task_to_relation_layers_map
    )

    _replace_multilevel_hierarchies_with_single_level_dummies(
        get_unique_dummy_task=get_unique_dummy_task,
        graph=graph_with_dummies,
        task_to_relation_layers_map=task_or_dummy_to_scaled_relation_layers_map,
    )

    _replace_multilevel_dependencies_with_single_level_dummies(
        get_unique_dummy_task=get_unique_dummy_task,
        graph=graph_with_dummies,
        task_to_relation_layers_map=task_or_dummy_to_scaled_relation_layers_map,
    )

    return graph_with_dummies, task_or_dummy_to_scaled_relation_layers_map
