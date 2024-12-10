import tkinter as tk

from graft import architecture
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import event_broker
from graft.layers.presentation.tkinter_gui.helpers.colour import (
    BLACK,
    BLUE,
    GREEN,
    YELLOW,
    Colour,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.relationship_drawing_properties import (
    RelationshipDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.static_task_network_graph import (
    DEFAULT_STANDARD_DEPENDENCY_COLOUR,
    DEFAULT_STANDARD_HIERARCHY_COLOUR,
    DEFAULT_STANDARD_RELATIONSHIP_ALPHA,
    StaticTaskNetworkGraph,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.task_drawing_properties import (
    TaskDrawingProperties,
)


def _format_task_name_for_annotation(name: tasks.Name) -> str | None:
    """Helper function to transform a task name into the form expected by annotation text."""
    return str(name) if name else None


class ProgressGraph(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        # TODO: Highlight selected task somehow
        super().__init__(master=master)

        self._logic_layer = logic_layer
        self._selected_task: tasks.UID | None = None

        self._static_graph = StaticTaskNetworkGraph(
            master=self,
            graph=tasks.NetworkGraph.empty(),
            get_task_annotation_text=self._get_formatted_task_name,
            get_task_properties=self._get_task_properties,
            get_hierarchy_properties=lambda _, __: RelationshipDrawingProperties(
                colour=DEFAULT_STANDARD_HIERARCHY_COLOUR,
                alpha=DEFAULT_STANDARD_RELATIONSHIP_ALPHA,
            ),
            get_dependency_properties=lambda _, __: RelationshipDrawingProperties(
                colour=DEFAULT_STANDARD_DEPENDENCY_COLOUR,
                alpha=DEFAULT_STANDARD_RELATIONSHIP_ALPHA,
            ),
            on_node_left_click=self._publish_task_as_selected,
        )

        self._static_graph.grid(row=0, column=0)

        self._update_figure()

        broker = event_broker.get_singleton()
        broker.subscribe(
            event_broker.SystemModified, lambda _: self._on_system_modified()
        )
        broker.subscribe(event_broker.TaskSelected, self._on_task_selected)

    def _on_system_modified(self) -> None:
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
        return _format_task_name_for_annotation(name)

    def _get_task_colour(self, task: tasks.UID) -> Colour:
        # TODO: Can make this more efficient by getting all task progresses at once
        match self._logic_layer.get_task_system().get_progress(task):
            case tasks.Progress.NOT_STARTED:
                return BLUE
            case tasks.Progress.IN_PROGRESS:
                return YELLOW
            case tasks.Progress.COMPLETED:
                return GREEN

    def _get_task_properties(self, task: tasks.UID) -> TaskDrawingProperties:
        colour = self._get_task_colour(task)
        return TaskDrawingProperties(colour=colour, label_colour=BLACK)

    def _publish_task_as_selected(self, task: tasks.UID) -> None:
        broker = event_broker.get_singleton()
        broker.publish(event_broker.TaskSelected(task=task))

    def _update_figure(self) -> None:
        self._static_graph.update_graph(
            graph=self._logic_layer.get_task_system().network_graph(),
        )
