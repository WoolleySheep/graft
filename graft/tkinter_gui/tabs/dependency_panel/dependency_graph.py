import tkinter as tk

import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib import backend_bases as mpl_backend_bases
from matplotlib import collections as mpl_collections
from matplotlib import text as mpl_text
from matplotlib.backends import backend_tkagg

from graft import architecture
from graft.domain import tasks
from graft.tkinter_gui import event_broker, layered_graph_drawing
from graft.tkinter_gui.helpers import graph_conversion

GRAPH_ORIENTATION = layered_graph_drawing.GraphOrientation.HORIZONTAL


class DependencyGraph(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master)

        mpl.use("Agg")
        self._logic_layer = logic_layer
        self._selected_task: tasks.UID | None = None
        self._fig = plt.figure()
        self._ax = self._fig.add_subplot()
        self._annotation = mpl_text.Annotation("", (0, 0), (20, 20))
        self._display_annotation_callback_id: int | None = None
        self._select_task_callback_id: int | None = None
        self._canvas = backend_tkagg.FigureCanvasTkAgg(self._fig, self)
        self._canvas.get_tk_widget().grid()
        self._task_positions = dict[tasks.UID, tuple[float, float]]()
        self._tasks_in_path_order = list[tasks.UID]()
        self._task_path_collection = mpl_collections.PathCollection([])

        self._update_figure()

        broker = event_broker.get_singleton()
        broker.subscribe(event_broker.SystemModified, self._on_system_modified)
        broker.subscribe(event_broker.TaskSelected, self._on_task_selected)

    def _on_system_modified(self, event: event_broker.Event) -> None:
        if not isinstance(event, event_broker.SystemModified):
            raise TypeError

        if (
            self._selected_task is not None
            and self._selected_task not in self._logic_layer.get_task_system()
        ):
            self._selected_task = None

        self._update_figure()

    def _on_task_selected(self, event: event_broker.Event) -> None:
        if not isinstance(event, event_broker.TaskSelected):
            raise TypeError

        if self._selected_task is None or event.task != self._selected_task:
            self._selected_task = event.task
            self._update_figure()

    def _update_figure(self) -> None:
        self._ax.clear()
        self._annotation = self._ax.annotate(
            "",
            xy=(0, 0),
            xytext=(20, 20),
            textcoords="offset points",
            bbox={"boxstyle": "round", "fc": "w"},
        )
        self._annotation.set_visible(False)

        dependency_graph = (
            self._logic_layer.get_task_system().network_graph().dependency_graph()
        )
        digraph = graph_conversion.convert_dependency_to_dag(graph=dependency_graph)
        networkx_graph = graph_conversion.convert_simple_digraph_to_nx_digraph(digraph)
        self._tasks_in_path_order: list[tasks.UID] = list(networkx_graph)

        self._task_positions = (
            layered_graph_drawing.calculate_node_positions_sugiyama_method(
                graph=digraph, orientation=GRAPH_ORIENTATION
            )
        )

        task_colours = [
            "red"
            if self._selected_task is not None and task == self._selected_task
            else "#1f78b4"
            for task in self._tasks_in_path_order
        ]

        self._task_path_collection: mpl_collections.PathCollection = (
            nx.draw_networkx_nodes(
                networkx_graph,
                pos=self._task_positions,
                node_color=task_colours,  # pyright: ignore [reportArgumentType] (node_colour also accepts array[str])
                ax=self._ax,
            )
        )

        nx.draw_networkx_edges(
            networkx_graph,
            pos=self._task_positions,
            ax=self._ax,
            connectionstyle="arc3,rad=0.1",
        )
        nx.draw_networkx_labels(networkx_graph, pos=self._task_positions, ax=self._ax)

        self._canvas.draw()

        if self._display_annotation_callback_id is not None:
            self._fig.canvas.mpl_disconnect(self._display_annotation_callback_id)
        self._display_annotation_callback_id = self._fig.canvas.mpl_connect(
            "motion_notify_event", self._display_annotation
        )

        if self._select_task_callback_id is not None:
            self._fig.canvas.mpl_disconnect(self._select_task_callback_id)
        self._select_task_callback_id = self._fig.canvas.mpl_connect(
            "button_release_event", self._select_task
        )

    def _select_task(self, event: mpl_backend_bases.Event) -> None:
        if not isinstance(event, mpl_backend_bases.MouseEvent):
            raise TypeError

        # If there are no paths in the path collection, the `contains`
        # method will throw a TypeError rather than returning a nice,
        # sensible 'false'. This check stops it, as when there are zero
        # tasks there will be zero paths.
        if (
            event.button is not mpl_backend_bases.MouseButton.LEFT
            or event.inaxes != self._ax
            or not self._tasks_in_path_order
        ):
            return

        contains, details = self._task_path_collection.contains(event)

        if not contains:
            return

        task: tasks.UID = self._tasks_in_path_order[details["ind"][0]]

        broker = event_broker.get_singleton()
        broker.publish(event_broker.TaskSelected(task=task))

    def _display_annotation(self, event: mpl_backend_bases.Event) -> None:
        if not isinstance(event, mpl_backend_bases.MouseEvent):
            raise TypeError

        if event.inaxes != self._ax:
            if self._annotation.get_visible():
                self._annotation.set_visible(False)
                self._canvas.draw_idle()
            return

        # If there are no paths in the path collection, the `contains`
        # method will throw a TypeError rather than returning a nice,
        # sensible 'false'. This check stops it, as when there are zero
        # tasks there will be zero paths.
        if not self._tasks_in_path_order:
            return

        contains, details = self._task_path_collection.contains(event)

        if not contains:
            if self._annotation.get_visible():
                self._annotation.set_visible(False)
                self._fig.canvas.draw_idle()
            return

        task: tasks.UID = self._tasks_in_path_order[details["ind"][0]]

        register = self._logic_layer.get_task_system().attributes_register()
        attributes = register[task]

        if not attributes.name:
            if self._annotation.get_visible():
                self._annotation.set_visible(False)
                self._canvas.draw_idle()
            return

        self._annotation.set_text(str(attributes.name) or "")
        self._annotation.xy = self._task_positions[task]

        self._annotation.set_visible(True)
        self._fig.canvas.draw_idle()
