import functools
import tkinter as tk
from collections.abc import Mapping
from typing import Self, Sequence

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

GRAPH_ORIENTATION = layered_graph_drawing.GraphOrientation.VERTICAL


class HierarchyGraph(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        def update_figure(self: Self) -> None:
            def draw_graph(
                self: Self,
                graph: nx.DiGraph,
                pos: Mapping[tasks.UID, tuple[float, float]],
            ) -> tuple[mpl_collections.PathCollection, list[tasks.UID]]:
                node_path_collection: mpl_collections.PathCollection = (
                    nx.draw_networkx_nodes(
                        graph,
                        pos=pos,
                        ax=self.ax,
                    )
                )
                nodes_in_path_order = list(graph)
                nx.draw_networkx_edges(
                    graph, pos=pos, ax=self.ax, connectionstyle="arc3,rad=0.1"
                )
                nx.draw_networkx_labels(networkx_graph, pos=pos, ax=self.ax)

                self.canvas.draw()

                return node_path_collection, nodes_in_path_order

            def display_annotation(
                event: mpl_backend_bases.Event,
                self: Self,
                task_path_collection: mpl_collections.PathCollection,
                tasks_in_path_order: Sequence[tasks.UID],
                annotation: mpl_text.Annotation,
            ) -> None:
                if not isinstance(event, mpl_backend_bases.MouseEvent):
                    raise TypeError

                if event.inaxes != self.ax:
                    if annotation.get_visible():
                        annotation.set_visible(False)
                        self.canvas.draw_idle()
                    return

                # If there are no paths in the path collection, the `contains`
                # method will throw a TypeError rather than returning a nice,
                # sensible 'false'. This check stops it, as when there are zero
                # tasks there will be zero paths.
                if not tasks_in_path_order:
                    return

                contains, details = task_path_collection.contains(event)

                if not contains:
                    if annotation.get_visible():
                        annotation.set_visible(False)
                        self.fig.canvas.draw_idle()
                    return

                task = tasks_in_path_order[details["ind"][0]]

                register = self.logic_layer.get_task_system().attributes_register()
                attributes = register[task]

                if attributes.name is None:
                    if annotation.get_visible():
                        annotation.set_visible(False)
                        self.canvas.draw_idle()
                    return

                annotation.set_text(str(attributes.name) or "")
                annotation.xy = pos[task]

                annotation.set_visible(True)
                self.fig.canvas.draw_idle()

            self.ax.clear()

            annotation = self.ax.annotate(
                "",
                xy=(0, 0),
                xytext=(20, 20),
                textcoords="offset points",
                bbox={"boxstyle": "round", "fc": "w"},
            )
            annotation.set_visible(False)

            hierarchy_graph = self.logic_layer.get_task_system().hierarchy_graph()
            digraph = graph_conversion.convert_hierarchy_to_reduced_dag(
                graph=hierarchy_graph
            )
            networkx_graph = graph_conversion.convert_simple_digraph_to_nx_digraph(
                digraph
            )

            pos = layered_graph_drawing.calculate_node_positions_sugiyama_method(
                graph=digraph, orientation=GRAPH_ORIENTATION
            )

            task_path_collection, tasks_in_path_order = draw_graph(
                self=self, graph=networkx_graph, pos=pos
            )

            if self._annotation_callback_id is not None:
                self.fig.canvas.mpl_disconnect(self._annotation_callback_id)
            self._annotation_callback_id = self.fig.canvas.mpl_connect(
                "motion_notify_event",
                functools.partial(
                    display_annotation,
                    self=self,
                    task_path_collection=task_path_collection,
                    tasks_in_path_order=tasks_in_path_order,
                    annotation=annotation,
                ),
            )

        super().__init__(master)

        mpl.use("Agg")
        self.logic_layer = logic_layer
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot()
        self.canvas = backend_tkagg.FigureCanvasTkAgg(self.fig, self)
        self._annotation_callback_id: int | None = None
        self.canvas.get_tk_widget().grid()

        update_figure(self)

        broker = event_broker.get_singleton()
        broker.subscribe(event_broker.SystemModified, lambda _: update_figure(self))
