from typing import MutableMapping, Protocol

from graft.domain import tasks


class LayerPosition:
    def __init__(
        self, dependency_layer_min: int, dependency_layer_max: int, hierarchy_layer: int
    ) -> None:
        self.dependency_layer_min = dependency_layer_min
        self.dependency_layer_max = dependency_layer_max
        self.hierarchy_layer = hierarchy_layer


class GetLayersFn(Protocol):
    def __call__(
        self, graph: tasks.INetworkGraphView
    ) -> MutableMapping[tasks.UID, LayerPosition]:
        ...
