import itertools
import math
from collections.abc import (
    Callable,
    Generator,
    Mapping,
    MutableMapping,
    Sequence,
)

from graft.domain import tasks
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
        # Needs to be like this so UIDs and DummyUIDs with the same number don't
        # evaluate as equal
        return isinstance(other, DummyUID) and int(self) == int(other)

    def __hash__(self) -> int:
        """Return hash of the UID number.

        Needs to be overridden explicitly as hash function defaults to None when
        equality dunder is overridden in subclass.
        """
        return super().__hash__()

    def __repr__(self) -> str:
        """Return string representation of dummy UID."""
        return f"dummy_uid({self._number!r})"


def _closest_element[T: float](sorted_sequence: Sequence[T], value: float) -> T:
    """Return the element in the sequence with the minimum absolute difference to value.

    The sequence must be sorted (ascending order).
    """
    if len(sorted_sequence) == 0:
        raise ValueError

    left_pointer = 0
    right_pointer = len(sorted_sequence) - 1

    closest_element = sorted_sequence[0]  # Could be any element in the array
    min_abs_difference = abs(value - closest_element)

    while left_pointer <= right_pointer:
        middle_pointer = left_pointer + (right_pointer - left_pointer) // 2
        middle_element = sorted_sequence[middle_pointer]
        difference = value - middle_element
        abs_difference = abs(difference)

        if abs_difference < min_abs_difference:
            min_abs_difference = abs_difference
            closest_element = middle_element

        if difference == 0:
            # Found the exact value we're looking for - no need to keep searching
            break
        if difference < 0:
            right_pointer = middle_pointer - 1
        elif difference > 0:
            left_pointer = middle_pointer + 1

    return closest_element


def _islice_for_sequences[T](
    sequence: Sequence[T],
    start: int | None = None,
    stop: int | None = None,
    step: int = 1,
) -> Generator[T, None, None]:
    """Return a generator that mimics the behaviour of a slice.

    Should be exactly the same as iter(sequence(slice(start, stop, step)))
    """
    if step == 0:
        raise ValueError

    if step > 0:
        if start is None:
            start = 0
        elif start >= len(sequence):
            return
        elif start < 0:
            start = max(len(sequence) + start, 0)

        if stop is None:
            stop = len(sequence)
        elif stop < 0:
            stop = max(len(sequence) + stop, 0)
        else:
            stop = min(stop, len(sequence))

    else:
        if start is None or start >= len(sequence):
            start = len(sequence) - 1
        elif start < 0:
            start = len(sequence) + start
            if start < 0:
                return

        if stop is None:
            stop = -1
        elif stop < 0:
            stop = max(len(sequence) + stop, -1)
        elif stop >= len(sequence):
            stop = len(sequence) - 1

    for i in range(start, stop, step):
        yield sequence[i]


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
    graph: tasks.UnconstrainedNetworkGraph,
    task_to_relation_layers_map: MutableMapping[tasks.UID, TaskRelationLayers],
) -> None:
    # These two data structures are used to allow very quick computations of the
    # layers that lie between a two layers. Use the dict to find the start & stop
    # indexes, then iterate over the subset of the sorted list
    sorted_hierarchy_layers = sorted(
        {layers.hierarchy for layers in task_to_relation_layers_map.values()}
    )
    hierarchy_layer_to_sorted_hierarchy_layers_index_map = {
        layer: index for index, layer in enumerate(sorted_hierarchy_layers)
    }

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

        supertask_layer = task_to_relation_layers_map[supertask].hierarchy
        subtask_layer = task_to_relation_layers_map[subtask].hierarchy

        supertask_layer_index_in_sorted_hierarchy_layers = (
            hierarchy_layer_to_sorted_hierarchy_layers_index_map[supertask_layer]
        )
        subtask_layer_index_in_sorted_hierarchy_layers = (
            hierarchy_layer_to_sorted_hierarchy_layers_index_map[subtask_layer]
        )

        dummy_tasks_replacing_current_hierarchy = list[DummyUID]()
        for hierarchy_layer in _islice_for_sequences(
            sorted_hierarchy_layers,
            subtask_layer_index_in_sorted_hierarchy_layers + 1,
            supertask_layer_index_in_sorted_hierarchy_layers,
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
    graph: tasks.UnconstrainedNetworkGraph,
    task_to_relation_layers_map: MutableMapping[tasks.UID, TaskRelationLayers],
) -> None:
    # These two data structures are used to allow very quick computations of the
    # layers that lie between a two layers. Use the dict to find the start & stop
    # indexes, then iterate over the subset of the sorted list
    sorted_dependency_layers = sorted(
        {layers.dependency.min for layers in task_to_relation_layers_map.values()}
    )
    dependency_layer_to_sorted_dependency_layers_index_map = {
        layer: index for index, layer in enumerate(sorted_dependency_layers)
    }

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

        dependee_task_layer = task_to_relation_layers_map[dependee_task].dependency.max
        dependent_task_layer = task_to_relation_layers_map[
            dependent_task
        ].dependency.min
        dependee_task_layer_index_in_sorted_dependency_layers = (
            dependency_layer_to_sorted_dependency_layers_index_map[dependee_task_layer]
        )
        dependent_task_layer_index_in_sorted_dependency_layers = (
            dependency_layer_to_sorted_dependency_layers_index_map[dependent_task_layer]
        )

        dummy_tasks_replacing_current_dependency = list[DummyUID]()
        for dependency_level in _islice_for_sequences(
            sorted_dependency_layers,
            dependee_task_layer_index_in_sorted_dependency_layers + 1,
            dependent_task_layer_index_in_sorted_dependency_layers,
        ):
            dummy_task = get_unique_dummy_task()
            dummy_tasks_replacing_current_dependency.append(dummy_task)
            graph.add_task(dummy_task)

            dependency_level_delta = (
                dependency_level
                - task_to_relation_layers_map[dependee_task].dependency.max
            )
            interpolated_hierarchy_level = (
                hierarchy_change_gradient * dependency_level_delta
                + task_to_relation_layers_map[dependee_task].hierarchy
            )

            closest_hierarchy_level = _closest_element(
                sorted_hierarchy_levels, interpolated_hierarchy_level
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
    graph: tasks.IUnconstrainedNetworkGraphView,
    task_to_relation_layers_map: Mapping[tasks.UID, TaskRelationLayers],
) -> tuple[
    tasks.UnconstrainedNetworkGraph, dict[tasks.UID | DummyUID, TaskRelationLayers]
]:
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

    graph_with_dummies = graph.clone()

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
