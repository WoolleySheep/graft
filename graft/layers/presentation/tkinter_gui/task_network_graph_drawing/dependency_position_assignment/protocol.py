from collections.abc import Mapping
from typing import Protocol

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.dependency_position_assignment.position import (
    DependencyLayers,
)


class GetDependencyPositions(Protocol):
    def __call__(
        self, graph: tasks.IUnconstrainedNetworkGraphView
    ) -> Mapping[tasks.UID, DependencyLayers]: ...
