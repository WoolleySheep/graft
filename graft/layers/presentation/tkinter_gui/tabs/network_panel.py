import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import event_broker, graph_colours, helpers


def format_task_name_for_annotation(name: tasks.Name) -> str | None:
    """Helper function to transform a task name into the form expected by annotation text."""
    return str(name) if name else None


def _publish_task_as_selected(task: tasks.UID) -> None:
    broker = event_broker.get_singleton()
    broker.publish(event_broker.TaskSelected(task=task))


class NetworkPanel(ttk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)

        self._logic_layer = logic_layer
        self._selected_task: tasks.UID | None = None

        self._static_graph = helpers.StaticTaskNetworkGraph(
            master=self,
            graph=tasks.NetworkGraph.empty(),
            get_task_annotation_text=self._get_formatted_task_name,
            get_task_colour=self._get_task_colour,
            get_task_label_colour=None,
            get_hierarchy_colour=None,
            get_dependency_colour=None,
            additional_hierarchies=None,
            additional_dependencies=None,
            on_node_left_click=_publish_task_as_selected,
            get_additional_hierarchy_colour=None,
            get_additional_dependency_colour=None,
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

    def _publish_task_as_selected(self, task: tasks.UID) -> None:
        broker = event_broker.get_singleton()
        broker.publish(event_broker.TaskSelected(task=task))

    def _get_task_colour(self, task: tasks.UID) -> str | None:
        return (
            graph_colours.HIGHLIGHTED_NODE_COLOUR
            if task == self._selected_task
            else None
        )

    def _update_figure(self) -> None:
        self._static_graph.update_graph(
            graph=self._logic_layer.get_task_system().network_graph()
        )
