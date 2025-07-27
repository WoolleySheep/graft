from collections.abc import Collection, Mapping, Sequence


def combine_node_positions[T](
    ordered_layers: Sequence[Collection[T]],
    intra_layer_positions: Mapping[T, float],
    layer_positions: Sequence[float],
) -> dict[T, tuple[float, float]]:
    node_positions = dict[T, tuple[float, float]]()
    for layer, layer_position in zip(ordered_layers, layer_positions, strict=False):
        for node in layer:
            node_positions[node] = (intra_layer_positions[node], layer_position)

    return node_positions
