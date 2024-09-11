import math
from collections.abc import Collection, Mapping, Sequence

_MIN_LAYER_HEIGHT = 3


def _get_max_layer_width[T](
    layers: Collection[Collection[T]], intra_layer_positions: Mapping[T, float]
) -> float:
    if len(layers) == 0:
        raise ValueError

    max_layer_width = 0
    for layer in layers:
        max_layer_value = max(intra_layer_positions[node] for node in layer)
        min_layer_value = min(intra_layer_positions[node] for node in layer)
        layer_width = max_layer_value - min_layer_value
        max_layer_width = max(max_layer_width, layer_width)

    return max_layer_width


def _get_layer_positions_equally_spaced_method(
    nlayers: int, graph_height: float
) -> list[float]:
    if nlayers == 0:
        raise ValueError

    if math.isclose(graph_height, 0):
        raise ValueError

    if nlayers == 1:
        return [0]

    layer_separation = graph_height / (nlayers - 1)
    return [idx * layer_separation for idx in range(nlayers)]


def get_layer_positions_max_width_fractions_method[T](
    intra_layer_positions: Mapping[T, float],
    ordered_layers: Sequence[Sequence[T]],
) -> list[float]:
    if len(ordered_layers) == 0:
        return []

    graph_height = _get_max_layer_width(
        layers=ordered_layers, intra_layer_positions=intra_layer_positions
    )

    # This happens when all the layers only have 1 node in them
    if math.isclose(graph_height, 0):
        graph_height = len(ordered_layers) * _MIN_LAYER_HEIGHT

    return _get_layer_positions_equally_spaced_method(
        nlayers=len(ordered_layers), graph_height=graph_height
    )
