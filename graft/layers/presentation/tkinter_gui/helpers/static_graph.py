import enum
import tkinter as tk
from collections.abc import (
    Callable,
    Hashable,
    Sequence,
    Set,
)
from typing import Final

import matplotlib as mpl
import networkx as nx
from matplotlib import backend_bases as mpl_backend_bases
from matplotlib import collections as mpl_collections
from matplotlib import patches
from matplotlib import pyplot as plt
from matplotlib import text as mpl_text
from matplotlib.artist import Artist
from matplotlib.backends import backend_tkagg
from matplotlib.legend import Legend
from matplotlib.legend_handler import HandlerBase
from matplotlib.patches import FancyArrowPatch
from matplotlib.transforms import Transform

from graft import graphs
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import (
    layered_graph_drawing,
)
from graft.layers.presentation.tkinter_gui.helpers import graph_conversion
from graft.layers.presentation.tkinter_gui.helpers.graph_edge_drawing_properties import (
    GraphEdgeDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.graph_node_drawing_properties import (
    GraphNodeDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.layered_graph_drawing.orientation import (
    GraphOrientation,
)
from graft.utils import group_by_hashable

_MOTION_NOTIFY_EVENT_NAME: Final = "motion_notify_event"
_BUTTON_RELEASE_EVENT_NAME: Final = "button_release_event"


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
        get_node_properties: Callable[[T], GraphNodeDrawingProperties],
        get_edge_properties: Callable[[T, T], GraphEdgeDrawingProperties],
        get_node_annotation_text: Callable[[T], str | None] | None = None,
        on_node_left_click: Callable[[T], None] | None = None,
        legend_elements: Sequence[
            tuple[str, GraphNodeDrawingProperties | GraphEdgeDrawingProperties]
        ]
        | None = None,
        additional_edges: Set[tuple[T, T]] | None = None,
        get_additional_edge_properties: Callable[[T, T], GraphEdgeDrawingProperties]
        | None = None,
    ) -> None:
        super().__init__(master)

        self._graph_orientation = graph_orientation
        self._graph = graph
        self._get_node_properties = get_node_properties
        self._get_edge_properties = get_edge_properties
        self._get_node_annotation_text = get_node_annotation_text
        self._legend_elements = legend_elements

        if (additional_edges is None) ^ (get_additional_edge_properties is None):
            raise ValueError

        self._additional_edges = additional_edges
        self._get_additional_edge_properties = get_additional_edge_properties

        mpl.use("Agg")
        self._fig = plt.figure()
        self._ax = self._fig.add_subplot()
        self._fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
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
        get_node_properties: Callable[[T], GraphNodeDrawingProperties] | None = None,
        get_edge_properties: Callable[[T, T], GraphEdgeDrawingProperties] | None = None,
        additional_edges: Set[tuple[T, T]]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        get_additional_edge_properties: Callable[[T, T], GraphEdgeDrawingProperties]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        get_node_annotation_text: Callable[[T], str | None]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        on_node_left_click: Callable[[T], None]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        legend_elements: Sequence[
            tuple[str, GraphNodeDrawingProperties | GraphEdgeDrawingProperties]
        ]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
    ) -> None:
        if (
            additional_edges is not DefaultSentinel.DEFAULT
            or get_additional_edge_properties is not DefaultSentinel.DEFAULT
        ):
            additional_edges_ = (
                additional_edges
                if additional_edges is not DefaultSentinel.DEFAULT
                else self._additional_edges
            )
            get_additional_edge_properties_ = (
                get_additional_edge_properties
                if get_additional_edge_properties is not DefaultSentinel.DEFAULT
                else self._get_additional_edge_properties
            )
            if (additional_edges_ is None) ^ (get_additional_edge_properties_ is None):
                raise ValueError

            self._additional_edges = additional_edges_
            self._get_additional_edge_properties = get_additional_edge_properties_

        if graph_orientation is not None:
            self._graph_orientation = graph_orientation

        if graph is not None:
            self._graph = graph

        if get_node_properties is not None:
            self._get_node_properties = get_node_properties

        if get_edge_properties is not None:
            self._get_edge_properties = get_edge_properties

        if get_node_annotation_text is not DefaultSentinel.DEFAULT:
            self._get_node_annotation_text = get_node_annotation_text

        if on_node_left_click is not DefaultSentinel.DEFAULT:
            self._on_node_left_click = on_node_left_click

        if legend_elements is not DefaultSentinel.DEFAULT:
            self._legend_elements = legend_elements

        self._update_figure()

    def _update_figure(self) -> None:
        # https://stackoverflow.com/questions/76277152/how-can-i-create-a-custom-arrow-shaped-legend-key
        # No, I don't understand why I need this arrow handler rubbish to make this
        # work. But I do, and I don't want to spend the time to work out how to not.
        class ArrowHandler(HandlerBase):
            def create_artists(
                self,
                legend: Legend,
                orig_handle: Artist,
                xdescent: float,
                ydescent: float,
                width: float,
                height: float,
                fontsize: float,
                trans: Transform,
            ):
                return [orig_handle]

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
        if self._additional_edges is not None:
            networkx_graph.add_edges_from(self._additional_edges)

        self._nodes_in_path_order: list[T] = list(networkx_graph)

        self._node_positions = (
            layered_graph_drawing.calculate_node_positions_sugiyama_method(
                graph=self._graph, orientation=self._graph_orientation
            )
        )

        node_colours = list[str]()
        node_edge_colours = list[str]()
        node_alphas = list[float]()
        node_label_colours = dict[T, str]()
        for node in networkx_graph.nodes:
            node_properties = self._get_node_properties(node)
            node_colours.append(str(node_properties.colour))
            node_edge_colours.append(str(node_properties.edge_colour))
            node_alphas.append(float(node_properties.alpha))
            node_label_colours[node] = str(node_properties.label_colour)

        self._nodes_path_collection: mpl_collections.PathCollection = (
            nx.draw_networkx_nodes(
                networkx_graph,
                pos=self._node_positions,
                node_color=node_colours,  # pyright: ignore [reportArgumentType] (node_colour also accepts array[str])
                edgecolors=node_edge_colours,
                alpha=node_alphas,
                ax=self._ax,
            )
        )

        edges_with_properties = list[
            tuple[tuple[tasks.UID, tasks.UID], GraphEdgeDrawingProperties]
        ]()
        for source, target in networkx_graph.edges:
            if (
                self._additional_edges is not None
                and (source, target) in self._additional_edges
            ):
                assert self._get_additional_edge_properties is not None
                get_edge_properties = self._get_additional_edge_properties
            else:
                get_edge_properties = self._get_edge_properties

            properties = get_edge_properties(source, target)  # pyright: ignore[reportUnknownArgumentType]
            edges_with_properties.append(((source, target), properties))  # pyright: ignore[reportUnknownArgumentType]

        for connection_style, edges_with_properties_group in group_by_hashable(
            edges_with_properties, key=lambda x: x[1].connection_style
        ).items():
            edges = [
                edges_with_properties[0]
                for edges_with_properties in edges_with_properties_group
            ]
            alphas = [
                float(edges_with_properties[1].alpha)
                for edges_with_properties in edges_with_properties_group
            ]
            colours = [
                str(edges_with_properties[1].colour)
                for edges_with_properties in edges_with_properties_group
            ]
            arrow_styles = [
                str(edges_with_properties[1].arrow_style)
                for edges_with_properties in edges_with_properties_group
            ]
            line_styles = [
                str(edges_with_properties[1].line_style)
                for edges_with_properties in edges_with_properties_group
            ]

            # Have to do draw_networkx_edges for each connectionstyle individually as
            # only one connectionstyle can be drawn at a time

            nx.draw_networkx_edges(
                networkx_graph,
                pos=self._node_positions,
                edgelist=edges,
                edge_color=colours,  # pyright: ignore[reportArgumentType]
                ax=self._ax,
                connectionstyle=str(connection_style),  # pyright: ignore[reportArgumentType]
                alpha=alphas,
                arrowstyle=arrow_styles,
                style=line_styles,  # pyright: ignore[reportArgumentType]
            )

        nx.draw_networkx_labels(
            networkx_graph,
            pos=self._node_positions,
            font_color=node_label_colours,  # pyright: ignore [reportArgumentType] (font_color also accepts dict[N, str])
            ax=self._ax,
        )

        if self._legend_elements is not None:
            legend_elements = list[patches.Circle | patches.FancyArrowPatch]()
            for label, element in self._legend_elements:
                if isinstance(element, GraphNodeDrawingProperties):
                    patch = patches.Circle(
                        (0, 0),
                        facecolor=str(element.colour),
                        edgecolor=str(element.edge_colour),
                        label=label,
                    )
                else:
                    patch = patches.FancyArrowPatch(
                        (0, 3),
                        (22, 3),
                        alpha=float(element.alpha),
                        arrowstyle=patches.ArrowStyle.Simple(
                            head_length=0.3,
                            head_width=0.3,
                            tail_width=0.05,
                        ),  # pyright: ignore[reportCallIssue]
                        color=str(element.colour),
                        label=label,
                        mutation_scale=20,
                    )
                legend_elements.append(patch)

            self._ax.legend(
                handles=legend_elements,
                handler_map={FancyArrowPatch: ArrowHandler()},
                loc="lower right",
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
