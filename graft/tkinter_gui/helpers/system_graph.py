import abc
import enum
import functools
import tkinter as tk
from collections.abc import Callable, Collection, Container, Sequence

import matplotlib as mpl
import networkx as nx
from matplotlib import axes
from matplotlib import backend_bases as mpl_backend_bases
from matplotlib import collections as mpl_collections
from matplotlib import pyplot as plt
from matplotlib import text as mpl_text
from matplotlib.backends import backend_tkagg

from graft import graphs
from graft.domain import tasks
from graft.tkinter_gui import layered_graph_drawing
from graft.tkinter_gui.helpers import graph_conversion

type Edge = tuple[tasks.UID, tasks.UID]


def _get_reduced_dag_from_hierarchy(
    system: tasks.System,
) -> graphs.ReducedDAG[tasks.UID]:
    """Return a reduced DAG from the system's hierarchy."""
    return graph_conversion.convert_hierarchy_to_reduced_dag(
        graph=system.hierarchy_graph_view()
    )


def _get_dag_from_dependency(
    system: tasks.System,
) -> graphs.DirectedAcyclicGraph[tasks.UID]:
    """Return a DAG from the system's dependency graph."""
    return graph_conversion.convert_dependency_to_dag(
        graph=system.dependency_graph_view()
    )


class GraphType(enum.Enum):
    HIERARCHY = (
        layered_graph_drawing.GraphOrientation.VERTICAL,
        _get_reduced_dag_from_hierarchy,
    )
    DEPENDENCY = (
        layered_graph_drawing.GraphOrientation.HORIZONTAL,
        _get_dag_from_dependency,
    )

    def __init__(
        self,
        orientation: layered_graph_drawing.GraphOrientation,
        get_graph: Callable[[tasks.System], graphs.DirectedAcyclicGraph[tasks.UID]],
    ) -> None:
        self.orientation = orientation
        self.get_graph = get_graph


def get_edge_colour_fn(
    highlighted_edges: Container[Edge], additional_edges: Container[Edge]
) -> Callable[[Edge], str]:
    """Return a function that returns the colour of an edge."""

    def wrapper(edge: Edge) -> str:
        if edge in highlighted_edges:
            return "red"
        if edge in additional_edges:
            return "orange"
        return "black"

    return wrapper


class SystemGraph(tk.Frame, abc.ABC):
    """tkinter frame showing either a Hierarchy or Dependency graph."""

    def __init__(
        self,
        master: tk.Misc,
        graph_type: GraphType,
        system: tasks.System,
        highlighted_tasks: Container[tasks.UID] | None = None,
        highlighted_edges: Container[Edge] | None = None,
        additional_edges: Collection[Edge] | None = None,
    ) -> None:
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

        if highlighted_tasks is None:
            highlighted_tasks = set[tasks.UID]()

        if highlighted_edges is None:
            highlighted_edges = set[Edge]()

        if additional_edges is None:
            additional_edges = set[Edge]()

        if any(edge in highlighted_edges for edge in additional_edges):
            raise ValueError("highlighted_edges and additional_edges cannot overlap")

        super().__init__(master=master)

        mpl.use("Agg")
        fig = plt.figure()
        ax = fig.add_subplot()
        canvas = backend_tkagg.FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().grid()

        graph = graph_type.get_graph(system)
        nx_graph = graph_conversion.convert_simple_digraph_to_nx_digraph(graph=graph)

        pos = layered_graph_drawing.calculate_node_positions_sugiyama_method(
            graph=graph, orientation=graph_type.orientation
        )

        annotation = ax.annotate(
            "",
            xy=(0, 0),
            xytext=(20, 20),
            textcoords="offset points",
            bbox={"boxstyle": "round", "fc": "w"},
        )
        annotation.set_visible(False)

        tasks_in_path_order = list[tasks.UID](nx_graph)
        task_colours = [
            "red" if task in highlighted_tasks else "blue"
            for task in tasks_in_path_order
        ]
        task_path_collection: mpl_collections.PathCollection = nx.draw_networkx_nodes(
            nx_graph,
            pos=pos,
            node_color=task_colours,  # type: ignore (edge colour also accepts array[str])
            ax=ax,
        )

        nx_graph.add_edges_from(additional_edges)
        get_edge_colour = get_edge_colour_fn(
            highlighted_edges=highlighted_edges, additional_edges=additional_edges
        )
        task_colours = [get_edge_colour(edge) for edge in nx_graph.edges]

        nx.draw_networkx_edges(
            nx_graph,
            pos=pos,
            ax=ax,
            edge_color=task_colours,  # type: ignore (edge colour also accepts array[str])
            connectionstyle="arc3,rad=0.1",
        )
        nx.draw_networkx_labels(nx_graph, pos=pos, ax=ax)

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
