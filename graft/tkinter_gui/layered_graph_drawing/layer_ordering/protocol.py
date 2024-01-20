from collections.abc import Collection, Hashable, Sequence
from typing import Protocol

from graft import graphs


class GetLayerOrdersFn(Protocol):
    def __call__[T: Hashable](
        self, graph: graphs.DirectedAcyclicGraph[T], layers: Sequence[Collection[T]]
    ) -> Sequence[Sequence[T]]:
        ...
