from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.layers_assignment.protocol import (
    LayerPosition,
)


def get_layers_unnamed_method(
    graph: tasks.INetworkGraphView,
) -> dict[tasks.UID, LayerPosition]:
    raise NotImplementedError
