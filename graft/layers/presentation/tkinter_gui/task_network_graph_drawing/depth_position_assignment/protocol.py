from collections.abc import Mapping
from typing import Protocol

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.position import (
    RelationPosition,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.radius import (
    Radius,
)


class GetDepthPositions(Protocol):
    def __call__(
        self,
        graph: tasks.INetworkGraphView,
        relation_positions: Mapping[tasks.UID, RelationPosition],
        task_cylinder_radius: Radius,
    ) -> Mapping[tasks.UID, float]:
        ...
