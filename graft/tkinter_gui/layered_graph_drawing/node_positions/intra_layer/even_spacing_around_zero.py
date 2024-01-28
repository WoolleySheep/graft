from collections.abc import Sequence


def get_node_positions_even_spacing_around_zero_method[T](
    ordered_layers: Sequence[Sequence[T]],
    starting_separation_ratio: float,
    min_node_separation_distance: float,
) -> dict[T, float]:
    if starting_separation_ratio < 1:
        raise ValueError

    node_positions = dict[T, float]()
    separation_distance = starting_separation_ratio * min_node_separation_distance
    for layer in ordered_layers:
        for idx, node in enumerate(layer):
            position = separation_distance * (idx - (len(layer) / 2))
            node_positions[node] = position

    return node_positions
