import enum
import tkinter as tk
from collections.abc import (
    Callable,
    Hashable,
    Set,
)
from typing import Any, Final, Literal

import matplotlib as mpl
import networkx as nx
from matplotlib import backend_bases as mpl_backend_bases
from matplotlib import collections as mpl_collections
from matplotlib import pyplot as plt
from matplotlib import text as mpl_text
from matplotlib.backends import backend_tkagg

from graft import graphs
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import graph_colours, layered_graph_drawing
from graft.layers.presentation.tkinter_gui.helpers import graph_conversion
from graft.layers.presentation.tkinter_gui.helpers.node_drawing_properties import (
    NodeDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.layered_graph_drawing.orientation import (
    GraphOrientation,
)

_MOTION_NOTIFY_EVENT_NAME: Final = "motion_notify_event"
_BUTTON_RELEASE_EVENT_NAME: Final = "button_release_event"


def _return_none(*_: tuple[Any, ...]) -> Literal[None]:
    return None


class DefaultSentinel(enum.Enum):
    """Sentinel for default values where None can't be used.

    Should only ever be one value, DEFAULT.
    """

    DEFAULT = enum.auto()


def format_task_name_for_annotation(name: tasks.Name) -> str | None:
    """Helper function to transform a task name into the form expected by annotation text."""
    return str(name) if name else None


class StaticGraph[T: Hashable](tk.Frame):
    """Tkinter frame showing a graph.

    Provides the following features:
    - Update the graph and how it is shown
    - Register a callback that is called when left click on node
    - Register a callback that is called and returns the text for display in
      an annotation bubble when hover over node
    """

    def __init__(
        self,
        master: tk.Misc,
        graph_orientation: GraphOrientation,
        graph: graphs.DirectedAcyclicGraph[T],
        get_node_annotation_text: Callable[[T], str | None] | None = None,
        get_node_properties: Callable[[T], NodeDrawingProperties | None] | None = None,
        get_edge_colour: Callable[[T, T], str | None] | None = None,
        additional_edges: Set[tuple[T, T]] | None = None,
        on_node_left_click: Callable[[T], None] | None = None,
        get_additional_edge_colour: Callable[[T, T], str | None] | None = None,
    ) -> None:
        super().__init__(master)

        self._graph_orientation = graph_orientation
        self._graph = graph

        self._get_node_annotation_text = get_node_annotation_text

        self._get_node_properties = (
            get_node_properties if get_node_properties is not None else _return_none
        )

        self._get_edge_colour = (
            get_edge_colour if get_edge_colour is not None else _return_none
        )

        self._additional_edges = (
            additional_edges if additional_edges is not None else set[tuple[T, T]]()
        )

        self._get_additional_edge_colour = (
            get_additional_edge_colour
            if get_additional_edge_colour is not None
            else _return_none
        )

        if not self._additional_edges.isdisjoint(graph.edges()):
            msg = "Additional edges found already in the graph"
            raise ValueError(msg)

        mpl.use("Agg")
        self._fig = plt.figure()
        self._ax = self._fig.add_subplot()
        self._canvas = backend_tkagg.FigureCanvasTkAgg(self._fig, self)
        self._canvas.get_tk_widget().grid()
        self._annotation = mpl_text.Annotation("", (0, 0))
        self._motion_notify_event_callback_id: int | None = None
        self._on_node_left_click = on_node_left_click
        self._button_release_event_callback_id: int | None = None

        self._nodes_in_path_order = list[T]()
        self._nodes_path_collection = mpl_collections.PathCollection([])
        self._node_positions = dict[T, tuple[float, float]]()

        self._update_figure()

    def update_graph(
        self,
        graph_orientation: GraphOrientation | None = None,
        graph: graphs.DirectedAcyclicGraph[T] | None = None,
        get_node_annotation_text: Callable[[T], str | None]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        get_node_properties: Callable[[T], NodeDrawingProperties | None]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        get_edge_colour: Callable[[T, T], str | None]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        on_node_left_click: Callable[[T], None]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        additional_edges: Set[tuple[T, T]]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        get_additional_edge_colour: Callable[[T, T], str | None]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
    ) -> None:
        if graph_orientation is not None:
            self._graph_orientation = graph_orientation

        if graph is not None:
            self._graph = graph

        if get_node_annotation_text is not DefaultSentinel.DEFAULT:
            self._get_node_annotation_text = get_node_annotation_text

        if get_node_properties is not DefaultSentinel.DEFAULT:
            self._get_node_properties = (
                get_node_properties if get_node_properties is not None else _return_none
            )

        if get_edge_colour is not DefaultSentinel.DEFAULT:
            self._get_edge_colour = (
                get_edge_colour if get_edge_colour is not None else _return_none
            )

        if on_node_left_click is not DefaultSentinel.DEFAULT:
            self._on_node_left_click = on_node_left_click

        if additional_edges is not DefaultSentinel.DEFAULT:
            self._additional_edges = (
                additional_edges if additional_edges is not None else set[tuple[T, T]]()
            )

        if get_additional_edge_colour is not DefaultSentinel.DEFAULT:
            self._get_additional_edge_colour = (
                get_additional_edge_colour
                if get_additional_edge_colour is not None
                else _return_none
            )

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

        networkx_graph = graph_conversion.convert_directed_graph_to_nx_digraph(
            graph=self._graph
        )
        networkx_graph.add_edges_from(self._additional_edges)
        self._nodes_in_path_order: list[T] = list(networkx_graph)

        node_colours = list[str]()
        node_edge_colours = list[str]()
        for node in networkx_graph.nodes:
            node_properties = self._get_node_properties(node)
            colour = (
                node_properties.colour
                if node_properties is not None and node_properties.colour is not None
                else graph_colours.DEFAULT_NODE_COLOUR
            )
            node_colours.append(colour)
            edge_colour = (
                node_properties.edge_colour
                if node_properties is not None
                and node_properties.edge_colour is not None
                else colour
            )
            node_edge_colours.append(edge_colour)

        edge_colours = list[str]()
        for source, target in networkx_graph.edges:
            get_colour = (
                self._get_additional_edge_colour
                if (source, target) in self._additional_edges
                else self._get_edge_colour
            )
            colour = get_colour(source, target)
            edge_colours.append(
                colour if colour is not None else graph_colours.DEFAULT_EDGE_COLOUR
            )

        self._node_positions = (
            layered_graph_drawing.calculate_node_positions_sugiyama_method(
                graph=self._graph, orientation=self._graph_orientation
            )
        )

        self._nodes_path_collection: mpl_collections.PathCollection = (
            nx.draw_networkx_nodes(
                networkx_graph,
                pos=self._node_positions,
                node_color=node_colours,  # pyright: ignore [reportArgumentType] (node_colour also accepts array[str])
                edgecolors=node_edge_colours,
                ax=self._ax,
            )
        )

        nx.draw_networkx_edges(
            networkx_graph,
            pos=self._node_positions,
            edge_color=edge_colours,  # pyright: ignore [reportArgumentType] (edge_colour also accepts array[str])
            ax=self._ax,
            connectionstyle="arc3,rad=0.1",
        )

        nx.draw_networkx_labels(
            networkx_graph,
            pos=self._node_positions,
            font_color=graph_colours.DEFAULT_TEXT_COLOUR,
            ax=self._ax,
        )

        self._canvas.draw()

        if self._motion_notify_event_callback_id is not None:
            self._fig.canvas.mpl_disconnect(self._motion_notify_event_callback_id)

        if self._get_node_annotation_text is not None:
            self._motion_notify_event_callback_id = self._fig.canvas.mpl_connect(
                _MOTION_NOTIFY_EVENT_NAME, self._on_motion_notify_event
            )

        if self._button_release_event_callback_id is not None:
            self._fig.canvas.mpl_disconnect(self._button_release_event_callback_id)

        if self._on_node_left_click is not None:
            self._button_release_event_callback_id = self._fig.canvas.mpl_connect(
                _BUTTON_RELEASE_EVENT_NAME, self._on_button_release_event
            )

    def _on_motion_notify_event(self, event: mpl_backend_bases.Event) -> None:
        if not isinstance(event, mpl_backend_bases.MouseEvent):
            raise TypeError

        if event.name != _MOTION_NOTIFY_EVENT_NAME:
            raise ValueError

        if event.inaxes != self._ax:
            if self._annotation.get_visible():
                self._annotation.set_visible(False)
                self._canvas.draw_idle()
            return

        # If there are no paths in the path collection, the `contains`
        # method will throw a TypeError rather than returning a nice,
        # sensible 'false'. This check stops it, as when there are zero
        # tasks there will be zero paths.
        if not self._nodes_in_path_order:
            return

        contains, details = self._nodes_path_collection.contains(event)

        if not contains:
            if self._annotation.get_visible():
                self._annotation.set_visible(False)
                self._canvas.draw_idle()
            return

        # Really shouldn't ever fail this check, as only register for motion
        # notify event if I have an annotiation-text function to call
        if self._get_node_annotation_text is None:
            # TODO: Add some kind of warning log
            return

        index_in_order_of_node_motion_is_over: int = details["ind"][0]
        node_motion_is_over = self._nodes_in_path_order[
            index_in_order_of_node_motion_is_over
        ]

        annotation_text = self._get_node_annotation_text(node_motion_is_over)

        if annotation_text is None:
            if self._annotation.get_visible():
                self._annotation.set_visible(False)
                self._canvas.draw_idle()
            return

        self._annotation.set_text(annotation_text)
        self._annotation.xy = self._node_positions[node_motion_is_over]

        self._annotation.set_visible(True)
        self._canvas.draw_idle()

    def _on_button_release_event(self, event: mpl_backend_bases.Event) -> None:
        if not isinstance(event, mpl_backend_bases.MouseEvent):
            raise TypeError

        if event.name != _BUTTON_RELEASE_EVENT_NAME:
            raise ValueError

        if (
            event.button is not mpl_backend_bases.MouseButton.LEFT
            or event.inaxes != self._ax
            or not self._nodes_in_path_order
        ):
            return

        # If there are no paths in the path collection, the `contains`
        # method will throw a TypeError rather than returning a nice,
        # sensible 'false'. This check stops it, as when there are zero
        # tasks there will be zero paths.
        contains, details = self._nodes_path_collection.contains(event)

        if not contains:
            return

        # Really shouldn't ever fail this check, as only register for motion
        # notify event if I have an annotiation-text function to call
        if self._on_node_left_click is None:
            # TODO: Add some kind of warning log
            return

        index_in_order_of_node_clicked: int = details["ind"][0]
        node_clicked: T = self._nodes_in_path_order[index_in_order_of_node_clicked]
        self._on_node_left_click(node_clicked)
