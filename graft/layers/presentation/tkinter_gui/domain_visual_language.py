import enum
from typing import Final

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.helpers.alpha import OPAQUE, Alpha
from graft.layers.presentation.tkinter_gui.helpers.arrow_style import (
    CURVE_FILLED_B,
    ArrowStyle,
)
from graft.layers.presentation.tkinter_gui.helpers.colour import (
    BLACK,
    BLUE,
    GREEN,
    GREY,
    LIGHT_BLUE,
    LIGHT_YELLOW,
    ORANGE,
    RED,
    YELLOW,
    Colour,
)
from graft.layers.presentation.tkinter_gui.helpers.connection_style import (
    ARC3,
    ARC3RAD2,
    ConnectionStyle,
)
from graft.layers.presentation.tkinter_gui.helpers.graph_edge_drawing_properties import (
    GraphEdgeDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.graph_node_drawing_properties import (
    GraphNodeDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.line_style import SOLID, LineStyle
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.network_task_drawing_properties import (
    NetworkTaskDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.relationship_drawing_properties import (
    NetworkRelationshipDrawingProperties,
)

DEFAULT_GRAPH_NODE_COLOUR: Final = Colour("#1f78b4")
DEFAULT_GRAPH_EDGE_COLOUR: Final = BLACK
DEFAULT_GRAPH_TEXT_COLOUR: Final = BLACK

# Hierarchies
NETWORK_HIERARCHY_COLOUR: Final = GREEN

# Dependencies
NETWORK_DEPENDENCY_COLOUR: Final = BLACK

# Default
DEFAULT_NETWORK_TASK_COLOUR: Final = BLUE

# Importance
HIGH_IMPORTANCE_COLOUR: Final = RED
MEDIUM_IMPORTANCE_COLOUR: Final = ORANGE
LOW_IMPORTANCE_COLOUR: Final = YELLOW

# Progress
COMPLETED_TASK_COLOUR: Final = GREEN
IN_PROGRESS_TASK_COLOUR: Final = YELLOW
NOT_STARTED_TASK_COLOUR: Final = BLUE

# Active
ACTIVE_CONCRETE_TASK_COLOUR: Final = YELLOW
ACTIVE_COMPOSITE_TASK_COLOUR: Final = LIGHT_YELLOW
DOWNSTREAM_TASK_COLOUR: Final = LIGHT_BLUE
INACTIVE_TASK_COLOUR: Final = GREY

# Alpha fading
VERY_FADED_NETWORK_TASK_ALPHA: Final = Alpha(0.5)
FADED_NETWORK_TASK_ALPHA: Final = Alpha(0.7)
DEFAULT_NETWORK_TASK_ALPHA = Alpha(0.9)
HIGHLIGHTED_NETWORK_TASK_ALPHA: Final = Alpha(0.95)
VERY_HIGHLIGHTED_NETWORK_TASK_ALPHA: Final = Alpha(0.98)

VERY_FADED_NETWORK_TASK_LABEL_ALPHA: Final = Alpha(0.85)
FADED_NETWORK_TASK_LABEL_ALPHA: Final = Alpha(0.9)
DEFAULT_NETWORK_TASK_LABEL_ALPHA: Final = Alpha(0.95)
HIGHLIGHTED_NETWORK_TASK_LABEL_ALPHA: Final = Alpha(0.98)
VERY_HIGHLIGHTED_NETWORK_TASK_LABEL_ALPHA: Final = Alpha(0.99)

VERY_FADED_NETWORK_RELATIONSHIP_ALPHA: Final = Alpha(0.5)
FADED_NETWORK_RELATIONSHIP_ALPHA: Final = Alpha(0.7)
DEFAULT_NETWORK_RELATIONSHIP_ALPHA: Final = Alpha(0.9)
HIGHLIGHTED_NETWORK_RELATIONSHIP_ALPHA: Final = Alpha(0.95)
VERY_HIGHLIGHTED_NETWORK_RELATIONSHIP_ALPHA: Final = Alpha(0.98)

VERY_FADED_GRAPH_NODE_ALPHA = Alpha(0.5)
FADED_GRAPH_NODE_ALPHA = Alpha(0.7)
DEFAULT_GRAPH_NODE_ALPHA: Final = OPAQUE

VERY_FADED_GRAPH_NODE_LABEL_ALPHA = Alpha(0.7)
FADED_GRAPH_NODE_LABEL_ALPHA = Alpha(0.8)
DEFAULT_GRAPH_NODE_LABEL_ALPHA: Final = OPAQUE

VERY_FADED_GRAPH_EDGE_ALPHA = Alpha(0.5)
FADED_GRAPH_EDGE_ALPHA = Alpha(0.7)
DEFAULT_GRAPH_EDGE_ALPHA: Final = OPAQUE

# Line curving
CURVED_ARROW_CONNECTION_STYLE: Final = ARC3RAD2


class GraphAlphaLevel(enum.Enum):
    VERY_FADED = enum.auto()
    FADED = enum.auto()
    DEFAULT = enum.auto()


def get_graph_node_alpha(level: GraphAlphaLevel) -> tuple[Alpha, Alpha]:
    match level:
        case GraphAlphaLevel.VERY_FADED:
            return VERY_FADED_GRAPH_NODE_ALPHA, VERY_FADED_GRAPH_NODE_LABEL_ALPHA
        case GraphAlphaLevel.FADED:
            return FADED_GRAPH_NODE_ALPHA, FADED_GRAPH_NODE_LABEL_ALPHA
        case GraphAlphaLevel.DEFAULT:
            return DEFAULT_GRAPH_NODE_ALPHA, DEFAULT_GRAPH_NODE_LABEL_ALPHA


def get_graph_edge_alpha(level: GraphAlphaLevel) -> Alpha:
    match level:
        case GraphAlphaLevel.VERY_FADED:
            return VERY_FADED_GRAPH_EDGE_ALPHA
        case GraphAlphaLevel.FADED:
            return FADED_GRAPH_EDGE_ALPHA
        case GraphAlphaLevel.DEFAULT:
            return DEFAULT_GRAPH_EDGE_ALPHA


def get_graph_node_properties(
    colour: Colour = DEFAULT_GRAPH_NODE_COLOUR,
    alpha_level: GraphAlphaLevel = GraphAlphaLevel.DEFAULT,
    label_colour: Colour = DEFAULT_GRAPH_TEXT_COLOUR,
    edge_colour: Colour | None = None,
) -> GraphNodeDrawingProperties:
    alpha, label_alpha = get_graph_node_alpha(alpha_level)
    return GraphNodeDrawingProperties(
        colour=colour,
        alpha=alpha,
        label_colour=label_colour,
        edge_colour=edge_colour,
        label_alpha=label_alpha,
    )


def get_graph_edge_properties(
    colour: Colour = DEFAULT_GRAPH_EDGE_COLOUR,
    alpha_level: GraphAlphaLevel = GraphAlphaLevel.DEFAULT,
    line_style: LineStyle = SOLID,
    connection_style: ConnectionStyle = ARC3,
    arrow_style: ArrowStyle = CURVE_FILLED_B,
) -> GraphEdgeDrawingProperties:
    alpha = get_graph_edge_alpha(alpha_level)
    return GraphEdgeDrawingProperties(
        colour=colour,
        alpha=alpha,
        line_style=line_style,
        connection_style=connection_style,
        arrow_style=arrow_style,
    )


class NetworkAlphaLevel(enum.Enum):
    VERY_FADED = enum.auto()
    FADED = enum.auto()
    DEFAULT = enum.auto()
    HIGHLIGHTED = enum.auto()
    VERY_HIGHLIGHTED = enum.auto()


def get_network_task_alphas(level: NetworkAlphaLevel) -> tuple[Alpha, Alpha]:
    match level:
        case NetworkAlphaLevel.VERY_FADED:
            return VERY_FADED_NETWORK_TASK_ALPHA, VERY_FADED_NETWORK_TASK_LABEL_ALPHA
        case NetworkAlphaLevel.FADED:
            return FADED_NETWORK_TASK_ALPHA, FADED_NETWORK_TASK_LABEL_ALPHA
        case NetworkAlphaLevel.DEFAULT:
            return DEFAULT_NETWORK_TASK_ALPHA, DEFAULT_NETWORK_TASK_LABEL_ALPHA
        case NetworkAlphaLevel.HIGHLIGHTED:
            return HIGHLIGHTED_NETWORK_TASK_ALPHA, HIGHLIGHTED_NETWORK_TASK_LABEL_ALPHA
        case NetworkAlphaLevel.VERY_HIGHLIGHTED:
            return (
                VERY_HIGHLIGHTED_NETWORK_TASK_ALPHA,
                VERY_HIGHLIGHTED_NETWORK_TASK_LABEL_ALPHA,
            )


def get_network_relationship_alpha(level: NetworkAlphaLevel) -> Alpha:
    match level:
        case NetworkAlphaLevel.VERY_FADED:
            return VERY_FADED_NETWORK_RELATIONSHIP_ALPHA
        case NetworkAlphaLevel.FADED:
            return FADED_NETWORK_RELATIONSHIP_ALPHA
        case NetworkAlphaLevel.DEFAULT:
            return DEFAULT_NETWORK_RELATIONSHIP_ALPHA
        case NetworkAlphaLevel.HIGHLIGHTED:
            return HIGHLIGHTED_NETWORK_RELATIONSHIP_ALPHA
        case NetworkAlphaLevel.VERY_HIGHLIGHTED:
            return VERY_HIGHLIGHTED_NETWORK_RELATIONSHIP_ALPHA


def get_network_task_properties(
    colour: Colour = DEFAULT_NETWORK_TASK_COLOUR,
    alpha_level: NetworkAlphaLevel = NetworkAlphaLevel.DEFAULT,
    edge_colour: Colour | None = None,
    label_colour: Colour = BLACK,
) -> NetworkTaskDrawingProperties:
    alpha, label_alpha = get_network_task_alphas(alpha_level)
    return NetworkTaskDrawingProperties(
        colour=colour,
        label_colour=label_colour,
        edge_colour=edge_colour,
        alpha=alpha,
        label_alpha=label_alpha,
    )


def _get_network_relationship_properties(
    colour: Colour,
    alpha_level: NetworkAlphaLevel = NetworkAlphaLevel.DEFAULT,
    line_style: LineStyle = SOLID,
    connection_style: ConnectionStyle = ARC3,
    arrow_style: ArrowStyle = CURVE_FILLED_B,
) -> NetworkRelationshipDrawingProperties:
    alpha = get_network_relationship_alpha(alpha_level)
    return NetworkRelationshipDrawingProperties(
        colour=colour,
        alpha=alpha,
        line_style=line_style,
        connection_style=connection_style,
        arrow_style=arrow_style,
    )


def get_network_hierarchy_properties(
    colour: Colour = NETWORK_HIERARCHY_COLOUR,
    alpha_level: NetworkAlphaLevel = NetworkAlphaLevel.DEFAULT,
    line_style: LineStyle = SOLID,
    connection_style: ConnectionStyle = ARC3,
    arrow_style: ArrowStyle = CURVE_FILLED_B,
) -> NetworkRelationshipDrawingProperties:
    return _get_network_relationship_properties(
        colour=colour,
        alpha_level=alpha_level,
        line_style=line_style,
        connection_style=connection_style,
        arrow_style=arrow_style,
    )


def get_network_dependency_properties(
    colour: Colour = NETWORK_DEPENDENCY_COLOUR,
    alpha_level: NetworkAlphaLevel = NetworkAlphaLevel.DEFAULT,
    line_style: LineStyle = SOLID,
    connection_style: ConnectionStyle = ARC3,
    arrow_style: ArrowStyle = CURVE_FILLED_B,
) -> NetworkRelationshipDrawingProperties:
    return _get_network_relationship_properties(
        colour=colour,
        alpha_level=alpha_level,
        line_style=line_style,
        connection_style=connection_style,
        arrow_style=arrow_style,
    )


def get_task_colour_by_importance(importance: tasks.Importance | None) -> Colour:
    match importance:
        case tasks.Importance.HIGH:
            return HIGH_IMPORTANCE_COLOUR
        case tasks.Importance.MEDIUM:
            return MEDIUM_IMPORTANCE_COLOUR
        case tasks.Importance.LOW:
            return LOW_IMPORTANCE_COLOUR
        case None:
            return DEFAULT_GRAPH_NODE_COLOUR


def get_task_colour_by_progress(progress: tasks.Progress) -> Colour:
    match progress:
        case tasks.Progress.COMPLETED:
            return COMPLETED_TASK_COLOUR
        case tasks.Progress.IN_PROGRESS:
            return IN_PROGRESS_TASK_COLOUR
        case tasks.Progress.NOT_STARTED:
            return NOT_STARTED_TASK_COLOUR
