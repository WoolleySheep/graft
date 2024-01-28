from collections.abc import Collection, Mapping, Sequence


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
        if layer_width > max_layer_width:
            max_layer_width = layer_width

    return max_layer_width


def _get_layer_positions_max_width_fractions_method(
    nlayers: int, max_layer_width: float
) -> list[float]:
    if nlayers == 0:
        raise ValueError

    if nlayers == 1:
        return [0]

    layer_separation = max_layer_width / (nlayers - 1)
    return [idx * layer_separation for idx in range(nlayers)]


def get_layer_positions_max_width_fractions_method[T](
    intra_layer_positions: Mapping[T, float],
    ordered_layers: Sequence[Sequence[T]],
) -> list[float]:
    if len(ordered_layers) == 0:
        return []

    max_layer_width = _get_max_layer_width(
        layers=ordered_layers, intra_layer_positions=intra_layer_positions
    )
    return _get_layer_positions_max_width_fractions_method(
        nlayers=len(ordered_layers), max_layer_width=max_layer_width
    )
