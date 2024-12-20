from collections.abc import Hashable, Mapping

from graft import graphs

MIN_COMPONENT_SEPARATION_DISTANCE = 2


class ComponentPositionLimits:
    """The extremes of the positions of nodes within a component."""

    def __init__(self, min_: float, max_: float) -> None:
        if min_ > max_:
            msg = "min must be less than or equal to max"
            raise ValueError(msg)

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


def get_node_positions_inter_component_adjustment[T: Hashable](
    graph: graphs.DirectedAcyclicGraph[T],
    node_positions: Mapping[T, float],
    component_separation_distance: float,
) -> dict[T, float]:
    """Adjust the position of components of the graph relative to one another.

    Disconnected components of the graph tended to drift away from each other
    during positioning. This step aims to bring them back together without
    affecting the positioning of nodes relative to other nodes within the same
    component.
    """
    if component_separation_distance <= 0:
        msg = "component_separation_distance must be positive"
        raise ValueError(msg)

    if not graph:
        return {}

    components_with_limits = (
        (
            component,
            ComponentPositionLimits(
                min_=min(node_positions[node] for node in component.nodes()),
                max_=max(node_positions[node] for node in component.nodes()),
            ),
        )
        for component in graph.components()
    )

    components_with_limits_sorted_by_min_position = sorted(
        components_with_limits,
        key=lambda component_with_limits: component_with_limits[1].min,
    )

    node_to_adjusted_position_map = dict[T, float]()
    previous_component_max_position = 0  # Starting point is irrelevant
    for component, limits in components_with_limits_sorted_by_min_position:
        adjusted_min_position = (
            previous_component_max_position + MIN_COMPONENT_SEPARATION_DISTANCE
        )
        position_offset = adjusted_min_position - limits.min

        for node in component.nodes():
            node_to_adjusted_position_map[node] = node_positions[node] + position_offset

        previous_component_max_position = adjusted_min_position + limits.width

    return node_to_adjusted_position_map
