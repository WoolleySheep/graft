import tkinter as tk
from collections.abc import Callable, Set
from tkinter import ttk

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import graph_colours
from graft.layers.presentation.tkinter_gui.helpers.edge_drawing_properties import (
    EdgeDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.failed_operation_window import (
    OperationFailedWindow,
)
from graft.layers.presentation.tkinter_gui.helpers.node_drawing_properties import (
    NodeDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.static_hierarchy_graph import (
    StaticHierarchyGraph,
)


class HierarchyGraphOperationFailedWindow(OperationFailedWindow):
    def __init__(
        self,
        master: tk.Misc,
        description_text: str,
        hierarchy_graph: tasks.IHierarchyGraphView,
        get_task_annotation_text: Callable[[tasks.UID], str | None] | None = None,
        highlighted_tasks: Set[tasks.UID] | None = None,
        highlighted_hierarchies: Set[tuple[tasks.UID, tasks.UID]] | None = None,
        additional_hierarchies: Set[tuple[tasks.UID, tasks.UID]] | None = None,
    ) -> None:
        super().__init__(master=master)

        if highlighted_tasks is not None and not (
            highlighted_tasks <= hierarchy_graph.tasks()
        ):
            msg = "Some highlighted tasks not found graph"
            raise ValueError(msg)

        if highlighted_hierarchies is not None and not (
            highlighted_hierarchies <= hierarchy_graph.hierarchies()
        ):
            msg = "Some highlighted hierarchies not found graph"
            raise ValueError(msg)

        self._highlighted_tasks = (
            highlighted_tasks if highlighted_tasks is not None else set[tasks.UID]()
        )
        self._highlighted_hierarchies = (
            highlighted_hierarchies
            if highlighted_hierarchies is not None
            else set[tuple[tasks.UID, tasks.UID]]()
        )
        self._additional_hierarchies = (
            additional_hierarchies
            if additional_hierarchies is not None
            else set[tuple[tasks.UID, tasks.UID]]()
        )

        self._label = ttk.Label(self, text=description_text)

        self._graph = StaticHierarchyGraph(
            master=self,
            hierarchy_graph=hierarchy_graph,
            get_task_annotation_text=get_task_annotation_text,
            get_task_properties=self._get_task_properties,
            get_hierarchy_properties=self._get_hierarchy_properties,
            additional_hierarchies=additional_hierarchies,
            get_additional_hierarchy_properties=self._get_additional_hierarchy_properties,
        )

        self._label.grid(row=0, column=0)
        self._graph.grid(row=1, column=0)

    def _get_task_colour(self, task: tasks.UID) -> str:
        return (
            graph_colours.HIGHLIGHTED_NODE_COLOUR
            if task in self._highlighted_tasks
            else graph_colours.DEFAULT_NODE_COLOUR
        )

    def _get_task_properties(self, task: tasks.UID) -> NodeDrawingProperties:
        colour = self._get_task_colour(task)
        edge_colour = None
        return NodeDrawingProperties(colour=colour, edge_colour=edge_colour)

    def _get_hierarchy_colour(self, supertask: tasks.UID, subtask: tasks.UID) -> str:
        return (
            graph_colours.HIGHLIGHTED_EDGE_COLOUR
            if (supertask, subtask) in self._highlighted_hierarchies
            else graph_colours.DEFAULT_EDGE_COLOUR
        )

    def _get_hierarchy_properties(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> EdgeDrawingProperties:
        colour = self._get_hierarchy_colour(supertask, subtask)
        connection_style = None
        return EdgeDrawingProperties(colour=colour, connection_style=connection_style)

    def _get_additional_hierarchy_colour(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> str:
        return (
            graph_colours.INTRODUCED_EDGE_COLOUR
            if (supertask, subtask) in self._additional_hierarchies
            else graph_colours.DEFAULT_EDGE_COLOUR
        )

    def _get_additional_hierarchy_properties(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> EdgeDrawingProperties:
        colour = self._get_additional_hierarchy_colour(supertask, subtask)
        connection_style = None
        return EdgeDrawingProperties(colour=colour, connection_style=connection_style)
