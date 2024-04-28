import functools
import tkinter as tk
from typing import Sequence

import matplotlib as mpl
import networkx as nx
from matplotlib import axes
from matplotlib import backend_bases as mpl_backend_bases
from matplotlib import collections as mpl_collections
from matplotlib import pyplot as plt
from matplotlib import text as mpl_text
from matplotlib.backends import backend_tkagg

from graft.domain import tasks
from graft.tkinter_gui import layered_graph_drawing
from graft.tkinter_gui.helpers import graph_conversion

GRAPH_ORIENTATION = layered_graph_drawing.GraphOrientation.VERTICAL


class HierarchyGraph(tk.Frame):
    def __init__(self, master: tk.Misc, system: tasks.System) -> None:
        def display_annotation(
            event: mpl_backend_bases.Event,
            ax: axes.Axes,
            canvas: backend_tkagg.FigureCanvasTkAgg,
            annotation: mpl_text.Annotation,
            task_path_collection: mpl_collections.PathCollection,
            tasks_in_path_order: Sequence[tasks.UID],
            register: tasks.AttributesRegisterView,
        ) -> None:
            if not isinstance(event, mpl_backend_bases.MouseEvent):
                raise TypeError

            if event.inaxes != ax:
                if annotation.get_visible():
                    annotation.set_visible(False)
                    canvas.draw_idle()
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
                    canvas.draw_idle()
                return

            task = tasks_in_path_order[details["ind"][0]]
            task_name = register[task].name

            if task_name is None:
                if annotation.get_visible():
                    annotation.set_visible(False)
                    canvas.draw_idle()
                return

            annotation.set_text(task_name)
            annotation.xy = pos[task]

            annotation.set_visible(True)
            # TODO: Improve performance by only redrawing when the task or task name changes
            canvas.draw_idle()

        super().__init__(master=master)

        mpl.use("Agg")
        fig = plt.figure()
        ax = fig.add_subplot()
        canvas = backend_tkagg.FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().grid()

        hierarchy_graph = system.hierarchy_graph_view()
        reduced_dag = graph_conversion.convert_hierarchy_to_reduced_dag(
            hierarchy_graph=hierarchy_graph
        )
        digraph = graph_conversion.convert_simple_digraph_to_nx_digraph(
            digraph=reduced_dag
        )

        pos = layered_graph_drawing.calculate_node_positions_sugiyama_method(
            graph=reduced_dag, orientation=GRAPH_ORIENTATION
        )

        annotation = ax.annotate(
            "",
            xy=(0, 0),
            xytext=(20, 20),
            textcoords="offset points",
            bbox={"boxstyle": "round", "fc": "w"},
        )
        annotation.set_visible(False)

        task_path_collection: mpl_collections.PathCollection = nx.draw_networkx_nodes(
            digraph,
            pos=pos,
            ax=ax,
        )
        tasks_in_path_order = list(digraph)
        nx.draw_networkx_edges(digraph, pos=pos, ax=ax, connectionstyle="arc3,rad=0.1")
        nx.draw_networkx_labels(digraph, pos=pos, ax=ax)

        canvas.draw()

        fig.canvas.mpl_connect(
            "motion_notify_event",
            functools.partial(
                display_annotation,
                ax=ax,
                canvas=canvas,
                annotation=annotation,
                task_path_collection=task_path_collection,
                tasks_in_path_order=tasks_in_path_order,
                register=system.attributes_register_view(),
            ),
        )
