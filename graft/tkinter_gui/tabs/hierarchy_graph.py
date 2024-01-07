import functools
import tkinter as tk
from typing import Self

import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib import backend_bases as mpl_backend_bases
from matplotlib import collections as mpl_collections
from matplotlib import text as mpl_text
from matplotlib.backends import backend_tkagg

from graft import architecture, graphs
from graft.domain import tasks
from graft.tkinter_gui import event_broker


def get_topological_layered_positions(
    graph: nx.DiGraph,
) -> dict[tasks.UID, tuple[float, float]]:
    # return nx.drawing.nx_pydot.graphviz_layout(graph, prog="dot", args="-Grankdir=LR")
    g = graphs.DirectedAcyclicGraph[tasks.UID]()
    for n in graph.nodes:
        g.add_node(n)
    for u, v in graph.edges:
        g.add_edge(u, v)

    positions = dict[tasks.UID, tuple[float, float]]()
    for layer_count, layer in enumerate(g.topological_sort_with_grouping()):
        nodes_in_layer = list(layer)
        seperation = 100 / len(nodes_in_layer)
        for node_count, node in enumerate(nodes_in_layer):
            positions[node] = (seperation * node_count, -layer_count * 25)

    return positions


class HierarchyGraph(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        def update_figure(self: Self) -> None:
            def convert_hierarchy_to_networkx_graph(
                hierarchy_graph: tasks.HierarchyGraphView,
            ) -> nx.DiGraph:
                networkx_graph = nx.DiGraph()
                for task in hierarchy_graph:
                    networkx_graph.add_node(task)

                for parent, child in hierarchy_graph.hierarchies():
                    networkx_graph.add_edge(parent, child)

                return networkx_graph

            def draw_graph(
                self: Self, graph: nx.DiGraph, pos: dict[tasks.UID, tuple[float, float]]
            ) -> mpl_collections.PathCollection:
                node_path_collection: mpl_collections.PathCollection = (
                    nx.draw_networkx_nodes(
                        graph,
                        pos=pos,
                        ax=self.ax,
                    )
                )
                nx.draw_networkx_edges(networkx_graph, pos=pos, ax=self.ax)
                nx.draw_networkx_labels(networkx_graph, pos=pos, ax=self.ax)

                self.canvas.draw()

                return node_path_collection

            def display_annotation(
                event: mpl_backend_bases.Event,
                self: Self,
                task_path_collection: mpl_collections.PathCollection,
                annotation: mpl_text.Annotation,
            ) -> None:
                if not isinstance(event, mpl_backend_bases.MouseEvent):
                    raise TypeError

                if event.inaxes != self.ax:
                    return

                contains, details = task_path_collection.contains(event)

                if not contains:
                    if annotation.get_visible():
                        annotation.set_visible(False)
                        self.fig.canvas.draw_idle()
                    return

                task = tasks.UID(int(details["ind"][0]))

                register = self.logic_layer.get_task_attributes_register_view()
                attributes = register[task]

                if attributes.name is None:
                    annotation.set_visible(False)
                    self.fig.canvas.draw_idle()
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

            hierarchy_graph = self.logic_layer.get_hierarchy_graph_view()
            networkx_graph = convert_hierarchy_to_networkx_graph(hierarchy_graph)

            pos = get_topological_layered_positions(networkx_graph)

            # TODO: Change to Sugiyama hierarchical layout. Networkx can't draw
            # hierarchical graphs without graphvis. Using hacked together
            # topological layering for now
            task_path_collection = draw_graph(self=self, graph=networkx_graph, pos=pos)

            self.fig.canvas.mpl_connect(
                "motion_notify_event",
                functools.partial(
                    display_annotation,
                    self=self,
                    task_path_collection=task_path_collection,
                    annotation=annotation,
                ),
            )

        super().__init__(master)

        mpl.use("Agg")
        self.logic_layer = logic_layer
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot()
        self.canvas = backend_tkagg.FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid()

        update_figure(self)

        broker = event_broker.get_singleton()
        broker.subscribe(
            event_broker.SystemModified, lambda _: update_figure(self))
