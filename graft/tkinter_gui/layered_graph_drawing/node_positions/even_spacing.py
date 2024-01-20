from collections.abc import Sequence

from graft.tkinter_gui.layered_graph_drawing.dummy_node import DummyNode


def _calculate_node_x_pos_even_spacing(node_idx: int, nnodes_in_layer: int) -> float:
    """Calculate the x position of a node in an evenly-spaced layer.

    The x position is calculated as the node's index in the layer divided by the
    number of nodes, leaving room as if there were one more (invisible) node on
    each side.
    """
    return (node_idx + 1) / (nnodes_in_layer + 1)


def get_node_positions_vertical_even_spacing_method[T](
    ordered_layers: Sequence[Sequence[T | DummyNode]],
) -> dict[T, tuple[float, float]]:
    node_positions = dict[T, tuple[float, float]]()
    for layer_idx, nodes in enumerate(ordered_layers):
        node_y_pos = -layer_idx / len(ordered_layers)
        for node_idx, node in enumerate(nodes):
            if isinstance(node, DummyNode):
                continue

            node_x_pos = _calculate_node_x_pos_even_spacing(node_idx, len(nodes))
            node_positions[node] = (node_x_pos, node_y_pos)

    return node_positions
