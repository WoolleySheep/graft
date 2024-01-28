import enum
from collections.abc import Hashable, Mapping
from typing import Protocol


class GraphOrientation(enum.Enum):
    VERTICAL = enum.auto()
    HORIZONTAL = enum.auto()


class PlaceNodesFn[T: Hashable](Protocol):
    def __call__(
        self, node_positions: Mapping[T, tuple[float, float]]
    ) -> dict[T, tuple[float, float]]:
        ...


def _place_nodes_in_vertical_orientation[T: Hashable](
    node_positions: Mapping[T, tuple[float, float]],
) -> dict[T, tuple[float, float]]:
    return {
        node: (intra_level_position, -level_position)
        for node, (intra_level_position, level_position) in node_positions.items()
    }


def _place_nodes_in_horizontal_orientation[T: Hashable](
    node_positions: Mapping[T, tuple[float, float]],
) -> dict[T, tuple[float, float]]:
    return {
        node: (level_position, -intra_level_position)
        for node, (intra_level_position, level_position) in node_positions.items()
    }


def get_place_nodes_fn(orientation: GraphOrientation) -> PlaceNodesFn:
    match orientation:
        case GraphOrientation.VERTICAL:
            return _place_nodes_in_vertical_orientation
        case GraphOrientation.HORIZONTAL:
            return _place_nodes_in_horizontal_orientation

    raise ValueError
