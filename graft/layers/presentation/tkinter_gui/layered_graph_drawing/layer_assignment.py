from collections.abc import Collection, Hashable, Sequence
from typing import Protocol

from graft import graphs


class GetLayersFn[T: Hashable](Protocol):
    def __call__(
        self, graph: graphs.DirectedAcyclicGraph[T]
    ) -> Sequence[Collection[T]]: ...


def get_layers_topological_grouping_method[T: Hashable](
    graph: graphs.DirectedAcyclicGraph[T],
) -> list[set[T]]:
    return list(graph.topologically_sorted_groups())
