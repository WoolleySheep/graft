from collections.abc import Mapping
from typing import Protocol

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.dependency_position_assignment.position import (
    DependencyPosition,
)


class GetDependencyPositions(Protocol):
    def __call__(
        self, graph: tasks.INetworkGraphView
    ) -> Mapping[tasks.UID, DependencyPosition]:
        ...
