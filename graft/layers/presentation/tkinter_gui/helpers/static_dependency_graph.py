import tkinter as tk
from collections.abc import Callable, Set

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.helpers import graph_conversion
from graft.layers.presentation.tkinter_gui.helpers.edge_drawing_properties import (
    EdgeDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.node_drawing_properties import (
    NodeDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.static_graph import (
    DefaultSentinel,
    StaticGraph,
)
from graft.layers.presentation.tkinter_gui.layered_graph_drawing.orientation import (
    GraphOrientation,
)


class StaticDependencyGraph(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        dependency_graph: tasks.IDependencyGraphView,
        get_task_annotation_text: Callable[[tasks.UID], str | None] | None = None,
        get_task_properties: Callable[[tasks.UID], NodeDrawingProperties | None]
        | None = None,
        get_dependency_properties: Callable[
            [tasks.UID, tasks.UID], EdgeDrawingProperties | None
        ]
        | None = None,
        on_task_left_click: Callable[[tasks.UID], None] | None = None,
        additional_dependencies: Set[tuple[tasks.UID, tasks.UID]] | None = None,
        get_additional_dependency_properties: Callable[
            [tasks.UID, tasks.UID], EdgeDrawingProperties | None
        ]
        | None = None,
    ) -> None:
        super().__init__(master=master)
        self._static_graph = StaticGraph(
            master=self,
            graph_orientation=GraphOrientation.HORIZONTAL,
            graph=graph_conversion.convert_dependency_to_dag(dependency_graph),
            get_node_annotation_text=get_task_annotation_text,
            get_node_properties=get_task_properties,
            get_edge_properties=get_dependency_properties,
            on_node_left_click=on_task_left_click,
            additional_edges=additional_dependencies,
            get_additional_edge_properties=get_additional_dependency_properties,
        )

        self._static_graph.grid(row=0, column=0)

    def update_graph(
        self,
        dependency_graph: tasks.IDependencyGraphView | None,
        get_task_annotation_text: Callable[[tasks.UID], str | None]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        get_task_properties: Callable[[tasks.UID], NodeDrawingProperties | None]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        get_dependency_properties: Callable[
            [tasks.UID, tasks.UID], EdgeDrawingProperties | None
        ]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        on_task_left_click: Callable[[tasks.UID], None]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        additional_dependencies: Set[tuple[tasks.UID, tasks.UID]]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        get_additional_dependency_properties: Callable[
            [tasks.UID, tasks.UID], EdgeDrawingProperties | None
        ]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
    ) -> None:
        self._static_graph.update_graph(
            graph=graph_conversion.convert_dependency_to_dag(dependency_graph)
            if dependency_graph is not None
            else None,
            get_node_annotation_text=get_task_annotation_text,
            get_node_properties=get_task_properties,
            get_edge_properties=get_dependency_properties,
            on_node_left_click=on_task_left_click,
            additional_edges=additional_dependencies,
            get_additional_edge_properties=get_additional_dependency_properties,
        )
