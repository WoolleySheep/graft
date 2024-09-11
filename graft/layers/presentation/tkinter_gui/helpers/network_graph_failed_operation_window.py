import tkinter as tk
from collections.abc import Callable, Set
from tkinter import ttk

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import graph_colours
from graft.layers.presentation.tkinter_gui.helpers.failed_operation_window import (
    OperationFailedWindow,
)
from graft.layers.presentation.tkinter_gui.helpers.static_dependency_graph import (
    StaticDependencyGraph,
)
from graft.layers.presentation.tkinter_gui.helpers.static_hierarchy_graph import (
    StaticHierarchyGraph,
)


class NetworkGraphOperationFailedWindow(OperationFailedWindow):
    def __init__(
        self,
        master: tk.Misc,
        description_text: str,
        task_network: tasks.NetworkGraph,
        get_task_annotation_text: Callable[[tasks.UID], str | None] | None = None,
        highlighted_tasks: Set[tasks.UID] | None = None,
        highlighted_hierarchies: Set[tuple[tasks.UID, tasks.UID]] | None = None,
        additional_hierarchies: Set[tuple[tasks.UID, tasks.UID]] | None = None,
        highlighted_dependencies: Set[tuple[tasks.UID, tasks.UID]] | None = None,
        additional_dependencies: Set[tuple[tasks.UID, tasks.UID]] | None = None,
    ) -> None:
        super().__init__(master=master)

        if highlighted_tasks is not None and not (
            highlighted_tasks <= task_network.tasks()
        ):
            msg = "Some highlighted tasks not found graph"
            raise ValueError(msg)

        if highlighted_hierarchies is not None and not (
            highlighted_hierarchies <= task_network.hierarchy_graph().hierarchies()
        ):
            msg = "Some highlighted hierarchies not found graph"
            raise ValueError(msg)

        if highlighted_dependencies is not None and not (
            highlighted_dependencies <= task_network.dependency_graph().dependencies()
        ):
            msg = "Some highlighted dependencies not found graph"
            raise ValueError(msg)

        self._highlighted_tasks = (
            highlighted_tasks if highlighted_tasks is not None else set[tasks.UID]()
        )

        self._highlighted_hierarchies = (
            highlighted_hierarchies
            if highlighted_hierarchies is not None
            else set[tuple[tasks.UID, tasks.UID]]()
        )

        self._highlighted_dependencies = (
            highlighted_dependencies
            if highlighted_dependencies is not None
            else set[tuple[tasks.UID, tasks.UID]]()
        )

        self._additional_hierarchies = (
            additional_hierarchies
            if additional_hierarchies is not None
            else set[tuple[tasks.UID, tasks.UID]]()
        )

        self._additional_dependencies = (
            additional_dependencies
            if additional_dependencies is not None
            else set[tuple[tasks.UID, tasks.UID]]()
        )

        self._description_label = ttk.Label(self, text=description_text)

        self._hierarchy_graph_label = ttk.Label(self, text="Hierarchy graph")
        self._hierarchy_graph = StaticHierarchyGraph(
            master=self,
            hierarchy_graph=task_network.hierarchy_graph(),
            get_task_annotation_text=get_task_annotation_text,
            get_task_colour=self._get_task_colour,
            get_hierarchy_colour=self._get_hierarchy_colour,
            additional_hierarchies=additional_hierarchies,
            get_additional_hierarchy_colour=self._get_additional_hierarchy_colour,
        )

        self._dependency_graph_label = ttk.Label(self, text="Dependency graph")
        self._dependency_graph = StaticDependencyGraph(
            master=self,
            dependency_graph=task_network.dependency_graph(),
            get_task_annotation_text=get_task_annotation_text,
            get_task_colour=self._get_task_colour,
            get_dependency_colour=self._get_dependency_colour,
            additional_dependencies=additional_dependencies,
            get_additional_dependency_colour=self._get_additional_dependency_colour,
        )

        self._description_label.grid(row=0, column=0, columnspan=2)
        self._hierarchy_graph_label.grid(row=1, column=0)
        self._hierarchy_graph.grid(row=2, column=0)
        self._dependency_graph_label.grid(row=1, column=1)
        self._dependency_graph.grid(row=2, column=1)

    def _get_task_colour(self, task: tasks.UID) -> str:
        return (
            graph_colours.HIGHLIGHTED_NODE_COLOUR
            if task in self._highlighted_tasks
            else graph_colours.DEFAULT_NODE_COLOUR
        )

    def _get_hierarchy_colour(self, supertask: tasks.UID, subtask: tasks.UID) -> str:
        return (
            graph_colours.HIGHLIGHTED_EDGE_COLOUR
            if (supertask, subtask) in self._highlighted_hierarchies
            else graph_colours.DEFAULT_EDGE_COLOUR
        )

    def _get_additional_hierarchy_colour(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> str:
        return (
            graph_colours.INTRODUCED_EDGE_COLOUR
            if (supertask, subtask) in self._additional_hierarchies
            else graph_colours.DEFAULT_EDGE_COLOUR
        )

    def _get_dependency_colour(self, supertask: tasks.UID, subtask: tasks.UID) -> str:
        return (
            graph_colours.HIGHLIGHTED_EDGE_COLOUR
            if (supertask, subtask) in self._highlighted_dependencies
            else graph_colours.DEFAULT_EDGE_COLOUR
        )

    def _get_additional_dependency_colour(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> str:
        return (
            graph_colours.INTRODUCED_EDGE_COLOUR
            if (supertask, subtask) in self._additional_dependencies
            else graph_colours.DEFAULT_EDGE_COLOUR
        )
