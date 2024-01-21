import itertools
from collections.abc import Collection, Container, Hashable, Mapping, Sequence

from graft import graphs
from graft.tkinter_gui.layered_graph_drawing.layer_ordering.utils import (
    calculate_nintersecting_edges_between_layers,
    get_edges_between_layers,
)


class HashableCollection[T](Hashable, Collection[T]):
    ...


class HashableSequence[T](Hashable, Sequence[T]):
    ...


class Result[T: Sequence[Sequence]]:
    def __init__(self) -> None:
        self.topologically_sorted_ordered_groups: T | None = None
        self.min_nintersecting_edges = float("inf")


def _calculate_group_orders_recursive[T](
    result: Result[Sequence[Sequence[T]]],
    nintersecting_edges: int,
    topologically_sorted_ordered_groups: Sequence[HashableSequence[T]],
    ordered_source_to_sorted_ordered_targets_map: Mapping[
        HashableSequence[T], tuple[HashableSequence[T], int]
    ],
) -> None:
    ordered_source_group = topologically_sorted_ordered_groups[-1]

    # Check if you've reached the final group - this is the base case
    if ordered_source_group not in ordered_source_to_sorted_ordered_targets_map:
        if nintersecting_edges < result.min_nintersecting_edges:
            result.min_nintersecting_edges = nintersecting_edges
            result.topologically_sorted_ordered_groups = (
                topologically_sorted_ordered_groups
            )
        return

    for (
        ordered_target_group,
        nintersecting_edges_with_target_group,
    ) in ordered_source_to_sorted_ordered_targets_map[ordered_source_group]:
        if (
            target_nintersecting_edges := nintersecting_edges
            + nintersecting_edges_with_target_group
        ) >= result.min_nintersecting_edges:
            continue

        tmp_topologically_sorted_ordered_groups = list(
            topologically_sorted_ordered_groups
        )
        tmp_topologically_sorted_ordered_groups.append(ordered_target_group)

        _calculate_group_orders_recursive(
            result,
            target_nintersecting_edges,
            tmp_topologically_sorted_ordered_groups,
            ordered_source_to_sorted_ordered_targets_map,
        )


def get_layer_orders_brute_force_method[T: Hashable](
    graph: graphs.DirectedAcyclicGraph[T],
    layers: Sequence[Collection[T]],
) -> list[tuple[T, ...]]:
    """Get intra-group orderings that produces a graph with the least intersecting edges.

    Assumes that all edges only go between subsequent groups. For example, group
    1 -> group 2 is fine, group 1 -> group 4 is NOT fine.

    Using alpha-beta pruning to try and minimise the calculation time. Assuming
    that it is more likely that a globally optimal solution will consist of
    group pairs that are themselves optimal. As such will evaluate each group
    pair in order of increasing number of intersecting edges between that pair.
    """
    source_layer_order_to_sorted_target_layer_orders_map = dict[
        tuple[T, ...], list[tuple[tuple[T, ...], int]]
    ]()

    for source_layer, target_layer in itertools.pairwise(layers):
        edges = get_edges_between_layers(graph, source_layer, target_layer)
        for source_layer_order in itertools.permutations(
            source_layer, len(source_layer)
        ):
            target_layer_orders = (
                (
                    target_layer_order,
                    calculate_nintersecting_edges_between_layers(
                        source_layer_order,
                        target_layer_order,
                        edges,
                    ),
                )
                for target_layer_order in itertools.permutations(
                    target_layer, len(target_layer)
                )
            )
            sorted_target_layer_orders = sorted(target_layer_orders, key=lambda x: x[1])

            source_layer_order_to_sorted_target_layer_orders_map[
                source_layer_order
            ] = sorted_target_layer_orders

    # Sort the top level groups by number of minimum intersecting edges Evaluate
    # them in this order. Know that the target layer orders are sorted, so just
    # need to check the first one to get the minimum intersecting edges.
    first_layer = layers[0]
    first_layer_orders = itertools.permutations(first_layer, len(first_layer))
    sorted_first_layer_orders = sorted(
        first_layer_orders,
        key=lambda ordered_layer: source_layer_order_to_sorted_target_layer_orders_map[
            ordered_layer
        ][0][1],
    )

    result = Result[list[tuple[T, ...]]]()
    for first_layer_order in sorted_first_layer_orders:
        _calculate_group_orders_recursive(
            result,
            0,
            [first_layer_order],
            source_layer_order_to_sorted_target_layer_orders_map,
        )

    return result.topologically_sorted_ordered_groups
