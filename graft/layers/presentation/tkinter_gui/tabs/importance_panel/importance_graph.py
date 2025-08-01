import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.domain.tasks.hierarchy_graph import HierarchyGraphView
from graft.layers.presentation.tkinter_gui import domain_visual_language, event_broker
from graft.layers.presentation.tkinter_gui.domain_visual_language import (
    GraphAlphaLevel,
    get_graph_node_properties,
    get_task_colour_by_importance,
)
from graft.layers.presentation.tkinter_gui.helpers import (
    StaticHierarchyGraph,
    format_task_name_for_annotation,
)
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

        self._show_completed_tasks = tk.BooleanVar()
        self._show_completed_tasks_checkbutton = ttk.Checkbutton(
            self,
            text="Show completed tasks",
            variable=self._show_completed_tasks,
            command=self._on_show_completed_tasks_button_toggled,
        )
        self._show_completed_tasks.set(False)

        self._static_graph = StaticHierarchyGraph(
            master=self,
            hierarchy_graph=tasks.HierarchyGraph(),
            get_task_properties=self._get_task_properties,
            get_hierarchy_properties=self._get_hierarchy_properties,
            get_task_annotation_text=self._get_formatted_task_name,
            on_task_left_click=_publish_task_as_selected,
        )

        self._show_completed_tasks_checkbutton.grid(row=0, column=0)
        self._static_graph.grid(row=1, column=0)

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
        return get_task_colour_by_importance(
            self._logic_layer.get_task_system().get_importance(task)
        )

    def _get_task_properties(self, task: tasks.UID) -> GraphNodeDrawingProperties:
        return get_graph_node_properties(
            colour=self._get_task_colour(task),
            alpha_level=GraphAlphaLevel.DEFAULT
            if task == self._selected_task
            else GraphAlphaLevel.FADED,
            edge_colour=BLACK if task == self._selected_task else None,
        )

    def _get_hierarchy_properties(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> GraphEdgeDrawingProperties:
        return domain_visual_language.get_graph_edge_properties(
            alpha_level=GraphAlphaLevel.DEFAULT
            if self._selected_task in {subtask, supertask}
            else GraphAlphaLevel.FADED
        )

    def _update_figure(self) -> None:
        self._static_graph.update_graph(self._get_tasks_matching_current_filter())

    def _get_tasks_matching_current_filter(self) -> HierarchyGraphView:
        return (
            (
                self._logic_layer.get_task_system()
                if self._show_completed_tasks.get()
                else tasks.get_incomplete_system(self._logic_layer.get_task_system())
            )
            .network_graph()
            .hierarchy_graph()
        )

    def _on_show_completed_tasks_button_toggled(self) -> None:
        self._update_figure()
