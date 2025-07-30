import tkinter as tk

from graft import architecture
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import event_broker
from graft.layers.presentation.tkinter_gui.domain_visual_language import (
    DEFAULT_GRAPH_EDGE_COLOUR,
    DEFAULT_NETWORK_TASK_COLOUR,
    HIGH_IMPORTANCE_COLOUR,
    LOW_IMPORTANCE_COLOUR,
    MEDIUM_IMPORTANCE_COLOUR,
)
from graft.layers.presentation.tkinter_gui.helpers import (
    StaticHierarchyGraph,
    format_task_name_for_annotation,
)
from graft.layers.presentation.tkinter_gui.helpers.alpha import OPAQUE, Alpha
from graft.layers.presentation.tkinter_gui.helpers.colour import BLACK, Colour
from graft.layers.presentation.tkinter_gui.helpers.graph_edge_drawing_properties import (
    GraphEdgeDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.graph_node_drawing_properties import (
    GraphNodeDrawingProperties,
)


def _publish_task_as_selected(task: tasks.UID) -> None:
    broker = event_broker.get_singleton()
    broker.publish(event_broker.TaskSelected(task=task))


class ImportanceGraph(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master)

        self._logic_layer = logic_layer
        self._selected_task: tasks.UID | None = None

        self._static_graph = StaticHierarchyGraph(
            master=self,
            hierarchy_graph=tasks.HierarchyGraph(),
            get_task_properties=self._get_task_properties,
            get_hierarchy_properties=self._get_hierarchy_properties,
            get_task_annotation_text=self._get_formatted_task_name,
            on_task_left_click=_publish_task_as_selected,
        )

        self._static_graph.grid(row=0, column=0)

        self._update_figure()

        broker = event_broker.get_singleton()
        broker.subscribe(event_broker.SystemModified, self._on_system_modified)
        broker.subscribe(event_broker.TaskSelected, self._on_task_selected)

    def _on_system_modified(self, event: event_broker.Event) -> None:
        if not isinstance(event, event_broker.SystemModified):
            raise TypeError

        if (
            self._selected_task is not None
            and self._selected_task not in self._logic_layer.get_task_system().tasks()
        ):
            self._selected_task = None

        self._update_figure()

    def _on_task_selected(self, event: event_broker.Event) -> None:
        if not isinstance(event, event_broker.TaskSelected):
            raise TypeError

        if self._selected_task is not None and event.task == self._selected_task:
            return

        self._selected_task = event.task
        self._update_figure()

    def _get_formatted_task_name(self, task: tasks.UID) -> str | None:
        name = self._logic_layer.get_task_system().attributes_register()[task].name
        return format_task_name_for_annotation(name)

    def _get_task_colour(self, task: tasks.UID) -> Colour:
        # TODO: Can make this more efficient by getting all task importances at once
        match self._logic_layer.get_task_system().get_importance(task):
            case None:
                return DEFAULT_NETWORK_TASK_COLOUR
            case tasks.Importance.LOW:
                return LOW_IMPORTANCE_COLOUR
            case tasks.Importance.MEDIUM:
                return MEDIUM_IMPORTANCE_COLOUR
            case tasks.Importance.HIGH:
                return HIGH_IMPORTANCE_COLOUR

    def _get_task_edge_colour(self, task: tasks.UID) -> str | None:
        if task == self._selected_task:
            return "green"

        return (
            "black"
            if self._logic_layer.get_task_system()
            .attributes_register()[task]
            .importance
            is not None
            else None
        )

    def _get_task_properties(self, task: tasks.UID) -> GraphNodeDrawingProperties:
        if task == self._selected_task:
            alpha = OPAQUE
            edge_colour = BLACK
        else:
            alpha = Alpha(0.7)
            edge_colour = None
        return GraphNodeDrawingProperties(
            colour=self._get_task_colour(task), alpha=alpha, edge_colour=edge_colour
        )

    def _get_hierarchy_properties(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> GraphEdgeDrawingProperties:
        alpha = OPAQUE if self._selected_task in {supertask, subtask} else Alpha(0.7)
        return GraphEdgeDrawingProperties(colour=DEFAULT_GRAPH_EDGE_COLOUR, alpha=alpha)

    def _update_figure(self) -> None:
        self._static_graph.update_graph(
            hierarchy_graph=self._logic_layer.get_task_system()
            .network_graph()
            .hierarchy_graph()
        )
