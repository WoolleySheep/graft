import enum
import tkinter as tk
from collections.abc import Callable, Set
from typing import TYPE_CHECKING, Any, Final, Literal

import matplotlib as mpl
from matplotlib import backend_bases, text
from matplotlib import pyplot as plt
from matplotlib.backends import backend_tkagg
from mpl_toolkits.mplot3d import art3d, axis3d, proj3d

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import (
    graph_colours,
    task_network_graph_drawing,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.arrow_3d import (
    Arrow3D,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.cylinder_plotting import (
    CylinderDrawingProperties,
    Label,
    LabelDrawingProperties,
    XAxisCylinderPosition,
    plot_x_axis_cylinder,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.relationship_drawing_properties import (
    RelationshipDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.task_drawing_properties import (
    TaskDrawingProperties,
)

if TYPE_CHECKING:
    from mpl_toolkits import mplot3d

_MOTION_NOTIFY_EVENT_NAME: Final = "motion_notify_event"
_BUTTON_RELEASE_EVENT_NAME: Final = "button_release_event"

_DEFAULT_HIERARCHY_ARROW_COLOUR: Final = "green"
_DEFAULT_DEPENDENCY_ARROW_COLOUR: Final = "black"

_DEFAULT_ADDITIONAL_HIERARCHY_ARROW_COLOUR: Final = "yellow"
_DEFAULT_ADDITIONAL_DEPENDENCY_ARROW_COLOUR: Final = "pink"

_AXIS_ARROW_COLOUR: Final = "black"


_TASK_CYLINDER_RADIUS: Final = 0.25
_TASK_CYLINDER_NUMBER_OF_POLYGONS: Final = 10
_TASK_CYLINDER_ALPHA: Final = 0.8
_TASK_LABEL_ALPHA: Final = 0.9


def _return_none(*args: Any, **kwargs: Any) -> Literal[None]:
    return None


def _remove_axis(axis: axis3d.Axis) -> None:
    axis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    axis._axinfo["grid"]["color"] = (1, 1, 1, 0)
    axis.set_ticks([])
    axis.line.set_color((1.0, 1.0, 1.0, 0.0))


class DefaultSentinel(enum.Enum):
    """Sentinel for default values where None can't be used.

    Should only ever be one value, DEFAULT.
    """

    DEFAULT = enum.auto()


class StaticTaskNetworkGraph(tk.Frame):
    """Tkinter frame showing a task network graph.

    Provides the following features:
    - Update the graph and how it is shown
    - Register a callback that is called when left click on node
    - Register a callback that is called and returns the text for display in
      an annotation bubble when hover over node
    """

    def __init__(
        self,
        master: tk.Misc,
        graph: tasks.INetworkGraphView,
        get_task_annotation_text: Callable[[tasks.UID], str | None] | None = None,
        get_task_properties: Callable[[tasks.UID], TaskDrawingProperties | None]
        | None = None,
        get_hierarchy_properties: Callable[
            [tasks.UID, tasks.UID], RelationshipDrawingProperties | None
        ]
        | None = None,
        get_dependency_properties: Callable[
            [tasks.UID, tasks.UID], RelationshipDrawingProperties | None
        ]
        | None = None,
        additional_hierarchies: Set[tuple[tasks.UID, tasks.UID]] | None = None,
        additional_dependencies: Set[tuple[tasks.UID, tasks.UID]] | None = None,
        on_node_left_click: Callable[[tasks.UID], None] | None = None,
        get_additional_hierarchy_properties: Callable[
            [tasks.UID, tasks.UID], RelationshipDrawingProperties | None
        ]
        | None = None,
        get_additional_dependency_properties: Callable[
            [tasks.UID, tasks.UID], RelationshipDrawingProperties | None
        ]
        | None = None,
    ) -> None:
        super().__init__(master)

        self._graph = graph
        self._task_positions: dict[tasks.UID, XAxisCylinderPosition] | None = None

        self._get_task_annotation_text = get_task_annotation_text

        self._get_task_properties = (
            get_task_properties if get_task_properties is not None else _return_none
        )

        self._get_hierarchy_properties = (
            get_hierarchy_properties
            if get_hierarchy_properties is not None
            else _return_none
        )

        self._get_dependency_properties = (
            get_dependency_properties
            if get_dependency_properties is not None
            else _return_none
        )

        self._additional_hierarchies = (
            additional_hierarchies
            if additional_hierarchies is not None
            else set[tuple[tasks.UID, tasks.UID]]()
        )

        if not self._additional_hierarchies.isdisjoint(
            self._graph.hierarchy_graph().hierarchies()
        ):
            msg = "Additional hierarchies must not overlap with graph hierarchies"
            raise ValueError(msg)

        self._additional_dependencies = (
            additional_dependencies
            if additional_dependencies is not None
            else set[tuple[tasks.UID, tasks.UID]]()
        )

        if not self._additional_dependencies.isdisjoint(
            self._graph.dependency_graph().dependencies()
        ):
            msg = "Additional dependencies must not overlap with graph dependencies"
            raise ValueError(msg)

        self._get_additional_hierarchy_properties = (
            get_additional_hierarchy_properties
            if get_additional_hierarchy_properties is not None
            else _return_none
        )

        self._get_additional_dependency_properties = (
            get_additional_dependency_properties
            if get_additional_dependency_properties is not None
            else _return_none
        )

        self._on_node_left_click = on_node_left_click

        mpl.use("Agg")
        self._fig = plt.figure()

        # An Axes3D is the returned type when the projection argument is
        # specified as "3d", hence the type ignore
        self._ax: mplot3d.Axes3D = self._fig.add_subplot(projection="3d")  # type: ignore[reportAttributeAccessIssue]

        self._canvas = backend_tkagg.FigureCanvasTkAgg(self._fig, self)
        self._canvas.get_tk_widget().grid()
        self._annotation = text.Annotation("", (0, 0))
        self._motion_notify_event_callback_id: int | None = None
        self._button_release_event_callback_id: int | None = None

        self._task_collections = list[tuple[tasks.UID, art3d.Poly3DCollection]]()

        self._update_figure()

    def update_graph(
        self,
        graph: tasks.INetworkGraphView | None = None,
        get_task_annotation_text: Callable[[tasks.UID], str | None]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        get_task_properties: Callable[[tasks.UID], TaskDrawingProperties | None]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        get_hierarchy_properties: Callable[
            [tasks.UID, tasks.UID], RelationshipDrawingProperties | None
        ]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        get_dependency_properties: Callable[
            [tasks.UID, tasks.UID], RelationshipDrawingProperties | None
        ]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        additional_hierarchies: Set[tuple[tasks.UID, tasks.UID]]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        additional_dependencies: Set[tuple[tasks.UID, tasks.UID]]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        on_node_left_click: Callable[[tasks.UID], None]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        get_additional_hierarchy_properties: Callable[
            [tasks.UID, tasks.UID], RelationshipDrawingProperties | None
        ]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        get_additional_dependency_properties: Callable[
            [tasks.UID, tasks.UID], RelationshipDrawingProperties | None
        ]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
    ) -> None:
        if graph is not None:
            self._graph = graph

        if get_task_annotation_text is not DefaultSentinel.DEFAULT:
            self._get_task_annotation_text = get_task_annotation_text

        if get_task_properties is not DefaultSentinel.DEFAULT:
            self._get_task_properties = (
                get_task_properties if get_task_properties is not None else _return_none
            )

        if get_hierarchy_properties is not DefaultSentinel.DEFAULT:
            self._get_hierarchy_properties = (
                get_hierarchy_properties
                if get_hierarchy_properties is not None
                else _return_none
            )

        if get_dependency_properties is not DefaultSentinel.DEFAULT:
            self._get_dependency_properties = (
                get_dependency_properties
                if get_dependency_properties is not None
                else _return_none
            )

        if additional_dependencies is not DefaultSentinel.DEFAULT:
            self._additional_dependencies = (
                additional_dependencies
                if additional_dependencies is not None
                else set[tuple[tasks.UID, tasks.UID]]()
            )

        if not self._additional_dependencies.isdisjoint(
            self._graph.dependency_graph().dependencies()
        ):
            msg = "Additional dependencies must not overlap with graph dependencies"
            raise ValueError(msg)

        if additional_hierarchies is not DefaultSentinel.DEFAULT:
            self._additional_hierarchies = (
                additional_hierarchies
                if additional_hierarchies is not None
                else set[tuple[tasks.UID, tasks.UID]]()
            )

        if not self._additional_hierarchies.isdisjoint(
            self._graph.hierarchy_graph().hierarchies()
        ):
            msg = "Additional hierarchies must not overlap with graph hierarchies"
            raise ValueError(msg)

        if on_node_left_click is not DefaultSentinel.DEFAULT:
            self._on_node_left_click = on_node_left_click

        if get_additional_hierarchy_properties is not DefaultSentinel.DEFAULT:
            self._get_additional_hierarchy_properties = (
                get_additional_hierarchy_properties
                if get_additional_hierarchy_properties is not None
                else _return_none
            )

        if get_additional_dependency_properties is not DefaultSentinel.DEFAULT:
            self._get_additional_dependency_properties = (
                get_additional_dependency_properties
                if get_additional_dependency_properties is not None
                else _return_none
            )

        self._update_figure()

    def _update_figure(self) -> None:
        # TODO: Consider keeping the current viewing perspective when updating
        # the figure; if you are zoomed in then click on a task to highlight it,
        # the whole view will zoom back out to the start, which is quite
        # annoying

        self._ax.clear()

        self._annotation = self._ax.annotate(
            "",
            xy=(0, 0),
            xytext=(10, 10),
            textcoords="offset points",
            bbox={"boxstyle": "round", "fc": "yellow"},
            zorder=20,
        )
        self._annotation.set_visible(False)

        self._task_collections.clear()

        tmp_task_positions = (
            task_network_graph_drawing.calculate_task_positions_unnamed_method(
                graph=self._graph,
                task_cylinder_radius=task_network_graph_drawing.Radius(
                    _TASK_CYLINDER_RADIUS
                ),
            )
        )
        self._task_positions = {
            task: XAxisCylinderPosition(
                x_min=position.min_dependency,
                x_max=position.max_dependency,
                y=position.depth,
                z=position.hierarchy,
            )
            for task, position in tmp_task_positions.items()
        }

        self._update_task_cylinders()
        self._update_hierarchy_arrows()
        self._update_dependency_arrows()
        self._update_additional_hierarchy_arrows()
        self._update_additional_dependency_arrows()

        self._update_legend()

        self.update_axis_arrows()

        self._ax.set_aspect("equal")

        self._canvas.draw()

        if self._motion_notify_event_callback_id is not None:
            self._fig.canvas.mpl_disconnect(self._motion_notify_event_callback_id)

        if self._get_task_annotation_text is not None:
            self._motion_notify_event_callback_id = self._fig.canvas.mpl_connect(
                _MOTION_NOTIFY_EVENT_NAME, self._on_motion_notify_event
            )

        if self._button_release_event_callback_id is not None:
            self._fig.canvas.mpl_disconnect(self._button_release_event_callback_id)

        if self._on_node_left_click is not None:
            self._button_release_event_callback_id = self._fig.canvas.mpl_connect(
                _BUTTON_RELEASE_EVENT_NAME, self._on_button_release_event
            )

    def _on_motion_notify_event(self, event: backend_bases.Event) -> None:
        assert self._task_positions is not None

        if not isinstance(event, backend_bases.MouseEvent):
            raise TypeError

        if event.name != _MOTION_NOTIFY_EVENT_NAME:
            raise ValueError

        if event.inaxes != self._ax:
            if self._annotation.get_visible():
                self._annotation.set_visible(False)
                self._canvas.draw_idle()
            return

        task_under_mouse = None
        for task, collection in self._task_collections:
            does_contain, _ = collection.contains(mouseevent=event)

            if does_contain:
                # Check if there is more than one task cylinder under the mouse; if
                # so, don't do anything
                if task_under_mouse is not None:
                    return

                task_under_mouse = task

        if task_under_mouse is None:
            if self._annotation.get_visible():
                self._annotation.set_visible(False)
                self._canvas.draw_idle()
            return

        # Really shouldn't ever fail this check, as only register for motion
        # notify event if I have an annotation-text function to call
        if self._get_task_annotation_text is None:
            return

        annotation_text = self._get_task_annotation_text(task_under_mouse)

        if annotation_text is None:
            if self._annotation.get_visible():
                self._annotation.set_visible(False)
                self._canvas.draw_idle()
            return

        self._annotation.set_text(annotation_text)
        task_position = self._task_positions[task_under_mouse]
        x_projection, y_projection, _ = proj3d.proj_transform(
            task_position.x_center,
            task_position.y,
            task_position.z,
            self._ax.get_proj(),
        )
        self._annotation.xy = (x_projection, y_projection)

        self._annotation.set_visible(True)
        self._canvas.draw_idle()

    def _on_button_release_event(self, event: backend_bases.Event) -> None:
        if not isinstance(event, backend_bases.MouseEvent):
            raise TypeError

        if event.name != _BUTTON_RELEASE_EVENT_NAME:
            raise ValueError

        if (
            event.button is not backend_bases.MouseButton.LEFT
            or event.inaxes != self._ax
        ):
            return

        task_under_mouse = None
        for task, collection in self._task_collections:
            does_contain, _ = collection.contains(mouseevent=event)

            if does_contain:
                # Check if there is more than one task cylinder under the mouse; if
                # so, don't do anything
                if task_under_mouse is not None:
                    return

                task_under_mouse = task

        if task_under_mouse is None:
            return

        # Really shouldn't ever fail this check, as only register for motion
        # notify event if I have an annotiation-text function to call
        if self._on_node_left_click is None:
            return

        self._on_node_left_click(task_under_mouse)

    def _update_task_cylinders(self) -> None:
        assert self._task_positions is not None

        for task, position in self._task_positions.items():
            properties = self._get_task_properties(task)
            colour = (
                properties.colour
                if properties is not None and properties.colour is not None
                else graph_colours.DEFAULT_NODE_COLOUR
            )
            alpha = (
                properties.alpha
                if properties is not None and properties.alpha is not None
                else _TASK_CYLINDER_ALPHA
            )

            task_cylinder_properties = CylinderDrawingProperties(
                colour=colour,
                number_of_polygons=_TASK_CYLINDER_NUMBER_OF_POLYGONS,
                alpha=alpha,
            )

            label_text = str(task)

            label_colour = (
                properties.label_colour
                if properties is not None and properties.label_colour is not None
                else graph_colours.DEFAULT_TEXT_COLOUR
            )

            label_alpha = (
                properties.label_alpha
                if properties is not None and properties.label_alpha is not None
                else _TASK_LABEL_ALPHA
            )

            label_properties = LabelDrawingProperties(
                colour=label_colour, alpha=label_alpha
            )

            collection = plot_x_axis_cylinder(
                ax=self._ax,
                radius=_TASK_CYLINDER_RADIUS,
                position=position,
                properties=task_cylinder_properties,
                label=Label(text=label_text, properties=label_properties),
            )

            self._task_collections.append((task, collection))

    def _update_hierarchy_arrows(self) -> None:
        assert self._task_positions is not None

        for supertask, subtask in self._graph.hierarchy_graph().hierarchies():
            supertask_position = self._task_positions[supertask]
            arrow_source_y = supertask_position.y
            arrow_source_z = supertask_position.z

            subtask_position = self._task_positions[subtask]
            arrow_x = subtask_position.x_center
            arrow_target_y = subtask_position.y
            arrow_target_z = subtask_position.z

            properties = self._get_additional_hierarchy_properties(supertask, subtask)

            colour = (
                properties.colour
                if properties is not None and properties.colour is not None
                else _DEFAULT_HIERARCHY_ARROW_COLOUR
            )

            arrow = Arrow3D(
                [arrow_x, arrow_x],
                [arrow_source_y, arrow_target_y],
                [arrow_source_z, arrow_target_z],
                arrowstyle="-|>",
                mutation_scale=10,
                color=colour,
            )

            self._ax.add_artist(arrow)

    def _update_dependency_arrows(self) -> None:
        assert self._task_positions is not None

        for (
            dependee_task,
            dependent_task,
        ) in self._graph.dependency_graph().dependencies():
            dependee_task_position = self._task_positions[dependee_task]
            arrow_source_x = dependee_task_position.x_max
            arrow_source_y = dependee_task_position.y
            arrow_source_z = dependee_task_position.z

            dependent_task_position = self._task_positions[dependent_task]
            arrow_target_x = dependent_task_position.x_min
            arrow_target_y = dependent_task_position.y
            arrow_target_z = dependent_task_position.z

            properties = self._get_dependency_properties(dependee_task, dependent_task)

            colour = (
                properties.colour
                if properties is not None and properties.colour is not None
                else _DEFAULT_DEPENDENCY_ARROW_COLOUR
            )

            arrow = Arrow3D(
                [arrow_source_x, arrow_target_x],
                [arrow_source_y, arrow_target_y],
                [arrow_source_z, arrow_target_z],
                arrowstyle="-|>",
                mutation_scale=10,
                color=colour,
            )
            self._ax.add_artist(arrow)

    def _update_additional_hierarchy_arrows(self) -> None:
        # TODO
        pass

    def _update_additional_dependency_arrows(self) -> None:
        # TODO
        pass

    def _update_legend(self) -> None:
        # TODO
        pass

    def update_axis_arrows(self) -> None:
        assert self._task_positions is not None

        self._ax.grid(False)

        for axis in [self._ax.xaxis, self._ax.yaxis, self._ax.zaxis]:
            _remove_axis(axis)

        if self._task_positions:
            x_min = float("inf")
            x_max = float("-inf")
            y_min = float("inf")
            y_max = float("-inf")
            z_min = float("inf")
            z_max = float("-inf")

            for task_position in self._task_positions.values():
                x_min = min(x_min, task_position.x_min)
                x_max = max(x_max, task_position.x_max)
                y_min = min(y_min, task_position.y - _TASK_CYLINDER_RADIUS)
                y_max = max(y_max, task_position.y + _TASK_CYLINDER_RADIUS)
                z_min = min(z_min, task_position.z - _TASK_CYLINDER_RADIUS)
                z_max = max(z_max, task_position.z + _TASK_CYLINDER_RADIUS)

            y = (y_min + y_max) / 2
        else:
            y = 0

            x_min = 0
            x_max = 1

            z_min = 0
            z_max = 1

        x_offset = 0.1 * (x_max - x_min)
        z_offset = 0.1 * (z_max - z_min)

        x_min -= x_offset
        x_max += x_offset

        z_min -= z_offset
        z_max += z_offset

        x_center = (x_min + x_max) / 2
        z_center = (z_min + z_max) / 2

        dependencies_arrow = Arrow3D(
            xs=(x_min, x_max),
            ys=(y, y),
            zs=(z_min, z_min),
            arrowstyle="-|>",
            mutation_scale=10,
            color=_AXIS_ARROW_COLOUR,
        )
        self._ax.add_artist(dependencies_arrow)

        self._ax.text(
            x_center,
            y,
            z_min - z_offset,
            "Dependencies",
            zdir="x",
            zorder=10,
        )

        hierarchies_arrow = Arrow3D(
            xs=(x_min, x_min),
            ys=(y, y),
            zs=(z_min, z_max),
            arrowstyle="-|>",
            mutation_scale=10,
            color=_AXIS_ARROW_COLOUR,
        )
        self._ax.add_artist(hierarchies_arrow)
        self._ax.text(
            x_min - x_offset,
            y,
            z_center,
            "Hierarchies",
            zdir="z",
            zorder=10,
        )
