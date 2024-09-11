from collections.abc import Collection, Sequence

from graft import graphs


def get_layer_orders_no_op_method[T](
    graph: graphs.DirectedAcyclicGraph[T],
    layers: Sequence[Collection[T]],
) -> list[list[T]]:
    return [list(layer) for layer in layers]
