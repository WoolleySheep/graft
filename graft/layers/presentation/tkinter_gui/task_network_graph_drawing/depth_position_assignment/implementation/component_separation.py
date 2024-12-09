from collections.abc import Mapping

from graft.domain import tasks

MIN_COMPONENT_SEPARATION_DISTANCE = 2


class ComponentPositionLimits:
    """The extremes of the positions of nodes within a component."""

    def __init__(self, min_: float, max_: float):
        if min_ > max_:
            raise ValueError("min must be less than or equal to max")

        self._min = min_
        self._max = max_

    @property
    def min(self) -> float:
        return self._min

    @property
    def max(self) -> float:
        return self._max

    @property
    def width(self) -> float:
        return self._max - self._min


def get_depth_positions_with_component_adjustment(
    graph: tasks.NetworkGraph,
    task_to_position_map: Mapping[tasks.UID, float],
    component_separation_distance: float,
) -> dict[tasks.UID, float]:
    """Adjust the position of components of the graph relative to one another.

    Disconnected components of the graph tended to drift away from each other
    during positioning. This step aims to bring them back together without
    affecting the positioning of tasks relative to other tasks within the same
    component.
    """
    if component_separation_distance <= 0:
        raise ValueError("component_separation_distance must be positive")

    if not graph:
        return {}

    components_with_limits = (
        (
            component,
            ComponentPositionLimits(
                min_=min(task_to_position_map[node] for node in component.tasks()),
                max_=max(task_to_position_map[node] for node in component.tasks()),
            ),
        )
        for component in graph.components()
    )

    components_with_limits_sorted_by_min_position = sorted(
        components_with_limits,
        key=lambda component_with_limits: component_with_limits[1].min,
    )

    task_to_adjusted_position_map = dict[tasks.UID, float]()
    previous_component_max_position = 0  # Starting point is irrelevant
    for component, limits in components_with_limits_sorted_by_min_position:
        adjusted_min_position = (
            previous_component_max_position + MIN_COMPONENT_SEPARATION_DISTANCE
        )
        position_offset = adjusted_min_position - limits.min

        for task in component.tasks():
            task_to_adjusted_position_map[task] = (
                task_to_position_map[task] + position_offset
            )

        previous_component_max_position = adjusted_min_position + limits.width

    return task_to_adjusted_position_map
