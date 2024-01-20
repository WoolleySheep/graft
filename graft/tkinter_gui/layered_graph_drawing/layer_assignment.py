from collections.abc import Collection, Hashable, Sequence
from typing import Protocol

from graft import graphs


class GetLayersFn(Protocol):
    def __call__[T: Hashable](
        self, graph: graphs.DirectedAcyclicGraph[T]
    ) -> Sequence[Collection[T]]:
        ...


def get_layers_topological_grouping_method[T](
    graph: graphs.DirectedAcyclicGraph[T],
) -> list[set[T]]:
    return list(graph.topological_sort_with_grouping())
