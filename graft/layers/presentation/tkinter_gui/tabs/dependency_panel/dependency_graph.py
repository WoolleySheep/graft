import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import domain_visual_language, event_broker
from graft.layers.presentation.tkinter_gui.helpers import (
    GraphNodeDrawingProperties,
    StaticDependencyGraph,
    format_task_name_for_annotation,
)
from graft.layers.presentation.tkinter_gui.helpers.colour import RED, Colour
from graft.layers.presentation.tkinter_gui.helpers.graph_edge_drawing_properties import (
    GraphEdgeDrawingProperties,
)


class DependencyGraph(tk.Frame):
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

        self._static_graph = StaticDependencyGraph(
            master=self,
            dependency_graph=tasks.DependencyGraph(),
            get_task_properties=self._get_task_properties,
            get_dependency_properties=self._get_dependency_properties,
            get_task_annotation_text=self._get_formatted_task_name,
            on_task_left_click=self._publish_task_as_selected,
            legend_elements=[
                (
                    "task",
                    GraphNodeDrawingProperties(
                        colour=domain_visual_language.DEFAULT_GRAPH_NODE_COLOUR
                    ),
                ),
                ("selected task", GraphNodeDrawingProperties(colour=RED)),
                (
                    "dependency",
                    GraphEdgeDrawingProperties(
                        colour=domain_visual_language.DEFAULT_GRAPH_EDGE_COLOUR
                    ),
                ),
            ],
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
        return (
            RED
            if task == self._selected_task
            else domain_visual_language.DEFAULT_GRAPH_NODE_COLOUR
        )

    def _get_task_properties(self, task: tasks.UID) -> GraphNodeDrawingProperties:
        return domain_visual_language.get_graph_node_properties(
            colour=self._get_task_colour(task)
        )

    def _get_dependency_properties(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> GraphEdgeDrawingProperties:
        return domain_visual_language.get_graph_edge_properties()

    def _publish_task_as_selected(self, task: tasks.UID) -> None:
        broker = event_broker.get_singleton()
        broker.publish(event_broker.TaskSelected(task=task))

    def _update_figure(self) -> None:
        self._static_graph.update_graph(
            dependency_graph=self._get_graph_matching_current_filter()
        )

    def _get_graph_matching_current_filter(self) -> tasks.DependencyGraphView:
        return (
            (
                self._logic_layer.get_task_system()
                if self._show_completed_tasks.get()
                else tasks.get_incomplete_system(self._logic_layer.get_task_system())
            )
            .network_graph()
            .dependency_graph()
        )

    def _on_show_completed_tasks_button_toggled(self) -> None:
        self._update_figure()
