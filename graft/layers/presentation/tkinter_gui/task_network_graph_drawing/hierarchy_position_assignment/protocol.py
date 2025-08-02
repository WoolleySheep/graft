from collections.abc import Mapping
from typing import Protocol

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.radius import (
    Radius,
)


class GetHierarchyLayers(Protocol):
    def __call__(
        self, graph: tasks.IUnconstrainedNetworkGraphView
    ) -> dict[tasks.UID, int]: ...


class GetHierarchyPositions(Protocol):
    def __call__(
        self,
        task_to_hierarchy_layer_map: Mapping[tasks.UID, int],
        task_cylinder_radius: Radius,
    ) -> dict[tasks.UID, float]: ...
