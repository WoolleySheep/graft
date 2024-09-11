import tkinter as tk
from collections.abc import Callable, Set
from tkinter import ttk

from graft.domain import tasks
from graft.tkinter_gui import graph_colours
from graft.tkinter_gui.helpers.failed_operation_window import OperationFailedWindow
from graft.tkinter_gui.helpers.static_dependency_graph import StaticDependencyGraph


class DependencyGraphOperationFailedWindow(OperationFailedWindow):
    def __init__(
        self,
        master: tk.Misc,
        description_text: str,
        dependency_graph: tasks.IDependencyGraphView,
        get_task_annotation_text: Callable[[tasks.UID], str | None] | None = None,
        highlighted_tasks: Set[tasks.UID] | None = None,
        additional_dependencies: Set[tuple[tasks.UID, tasks.UID]] | None = None,
    ) -> None:
        super().__init__(master=master)

        if highlighted_tasks is not None and not (
            highlighted_tasks <= dependency_graph.tasks()
        ):
            msg = "Some highlighted tasks not found graph"
            raise ValueError(msg)

        self._highlighted_tasks = (
            highlighted_tasks if highlighted_tasks is not None else set[tasks.UID]()
        )
        self._additional_dependencies = (
            additional_dependencies
            if additional_dependencies is not None
            else set[tuple[tasks.UID, tasks.UID]]()
        )

        self._label = ttk.Label(self, text=description_text)

        self._graph = StaticDependencyGraph(
            master=self,
            dependency_graph=dependency_graph,
            get_task_annotation_text=get_task_annotation_text,
            get_task_colour=self._get_task_colour,
            get_dependency_colour=self._get_dependency_colour,
            additional_dependencies=additional_dependencies,
            get_additional_dependency_colour=self._get_additional_dependency_colour,
        )

        self._label.grid(row=0, column=0)
        self._graph.grid(row=1, column=0)

    def _get_task_colour(self, task: tasks.UID) -> str:
        return (
            graph_colours.HIGHLIGHTED_NODE_COLOUR
            if task in self._highlighted_tasks
            else graph_colours.DEFAULT_NODE_COLOUR
        )

    def _get_dependency_colour(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> str:
        return graph_colours.DEFAULT_EDGE_COLOUR

    def _get_additional_dependency_colour(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> str:
        return (
            graph_colours.HIGHLIGHTED_EDGE_COLOUR
            if (dependee_task, dependent_task) in self._additional_dependencies
            else graph_colours.DEFAULT_EDGE_COLOUR
        )
