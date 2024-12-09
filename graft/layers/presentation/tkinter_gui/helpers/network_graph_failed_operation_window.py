import tkinter as tk
from collections.abc import Callable, Set
from tkinter import ttk
from typing import Final

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.helpers.failed_operation_window import (
    OperationFailedWindow,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.relationship_drawing_properties import (
    RelationshipDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.static_task_network_graph import (
    StaticTaskNetworkGraph,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.task_drawing_properties import (
    TaskDrawingProperties,
)

_NORMAL_TASK_COLOUR: Final = "blue"
_HIGHLIGHTED_TASK_COLOUR: Final = "red"
_STANDARD_HIERARCHY_COLOUR: Final = "green"
_STANDARD_DEPENDENCY_COLOUR: Final = "black"
_HIGHLIGHTED_HIERARCHY_COLOUR: Final = "orange"
_HIGHLIGHTED_DEPENDENCY_COLOUR: Final = "purple"
_ADDITIONAL_HIERARCHY_COLOUR: Final = "yellow"
_ADDITIONAL_DEPENDENCY_COLOUR: Final = "cyan"


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

        self._graph = StaticTaskNetworkGraph(
            master=self,
            graph=task_network,
            get_task_annotation_text=get_task_annotation_text,
            get_task_properties=self._get_task_properties,
            get_hierarchy_properties=self._get_hierarchy_properties,
            get_dependency_properties=self._get_dependency_properties,
            additional_hierarchies=self._additional_hierarchies,
            additional_dependencies=self._additional_dependencies,
            get_additional_hierarchy_properties=lambda _,
            __: RelationshipDrawingProperties(colour=_ADDITIONAL_HIERARCHY_COLOUR),
            get_additional_dependency_properties=lambda _,
            __: RelationshipDrawingProperties(colour=_ADDITIONAL_DEPENDENCY_COLOUR),
        )

        self._description_label.grid(row=0, column=0)
        self._graph.grid(row=1, column=0)

    def _get_task_properties(self, task: tasks.UID) -> TaskDrawingProperties:
        colour = self._get_task_colour(task)
        return TaskDrawingProperties(colour=colour)

    def _get_task_colour(self, task: tasks.UID) -> str:
        return (
            _HIGHLIGHTED_TASK_COLOUR
            if task in self._highlighted_tasks
            else _NORMAL_TASK_COLOUR
        )

    def _get_hierarchy_properties(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> RelationshipDrawingProperties:
        colour = self._get_hierarchy_colour(supertask, subtask)
        return RelationshipDrawingProperties(colour=colour)

    def _get_hierarchy_colour(self, supertask: tasks.UID, subtask: tasks.UID) -> str:
        return (
            _HIGHLIGHTED_HIERARCHY_COLOUR
            if (supertask, subtask) in self._highlighted_hierarchies
            else _STANDARD_HIERARCHY_COLOUR
        )

    def _get_dependency_properties(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> RelationshipDrawingProperties:
        colour = self._get_dependency_colour(supertask, subtask)
        return RelationshipDrawingProperties(colour=colour)

    def _get_dependency_colour(self, supertask: tasks.UID, subtask: tasks.UID) -> str:
        return (
            _HIGHLIGHTED_DEPENDENCY_COLOUR
            if (supertask, subtask) in self._highlighted_dependencies
            else _STANDARD_DEPENDENCY_COLOUR
        )
