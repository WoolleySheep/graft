import enum
import tkinter as tk
from collections.abc import Callable, Sequence, Set
from typing import TYPE_CHECKING, Final

import matplotlib as mpl
from matplotlib import backend_bases, text
from matplotlib import pyplot as plt
from matplotlib.artist import Artist
from matplotlib.backends import backend_tkagg
from matplotlib.legend import Legend
from matplotlib.legend_handler import HandlerBase
from matplotlib.patches import ArrowStyle, FancyArrowPatch, Patch
from matplotlib.transforms import Transform
from mpl_toolkits.mplot3d import art3d, axis3d, proj3d

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import (
    task_network_graph_drawing,
)
from graft.layers.presentation.tkinter_gui.helpers.colour import (
    BLACK,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.arrow_3d import (
    Arrow3D,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.cylinder_plotting import (
    CylinderDrawingProperties,
    CylinderLabel,
    CylinderLabelDrawingProperties,
    XAxisCylinderPosition,
    plot_x_axis_cylinder,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.network_task_drawing_properties import (
    NetworkTaskDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.relationship_drawing_properties import (
    NetworkRelationshipDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.radius import (
    Radius,
)

if TYPE_CHECKING:
    from mpl_toolkits import mplot3d

_AXIS_ARROW_COLOUR: Final = BLACK

_TASK_CYLINDER_RADIUS: Final = Radius(0.25)
_TASK_CYLINDER_NUMBER_OF_POLYGONS: Final = 10

_MOTION_NOTIFY_EVENT_NAME: Final = "motion_notify_event"
_BUTTON_RELEASE_EVENT_NAME: Final = "button_release_event"


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


class AdditionalRelationships:
    def __init__(
        self,
        relationships: Set[tuple[tasks.UID, tasks.UID]],
        get_relationship_properties: Callable[
            [tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties
        ],
    ) -> None:
        self._relationships = relationships
        self._get_relationship_properties = get_relationship_properties

    @property
    def relationships(self) -> Set[tuple[tasks.UID, tasks.UID]]:
        return self._relationships

    @property
    def get_relationship_properties(
        self,
    ) -> Callable[[tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties]:
        return self._get_relationship_properties


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
        graph: tasks.IUnconstrainedNetworkGraphView,
        get_task_annotation_text: Callable[[tasks.UID], str | None],
        get_task_properties: Callable[[tasks.UID], NetworkTaskDrawingProperties],
        get_hierarchy_properties: Callable[
            [tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties
        ],
        get_dependency_properties: Callable[
            [tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties
        ],
        additional_hierarchies: AdditionalRelationships | None = None,
        additional_dependencies: AdditionalRelationships | None = None,
        on_node_left_click: Callable[[tasks.UID], None] | None = None,
        legend_elements: Sequence[
            tuple[
                str, NetworkTaskDrawingProperties | NetworkRelationshipDrawingProperties
            ]
        ]
        | None = None,
    ) -> None:
        super().__init__(master)

        self._graph = graph
        self._task_positions: dict[tasks.UID, XAxisCylinderPosition] | None = None
        self._get_task_annotation_text = get_task_annotation_text
        self._get_task_properties = get_task_properties
        self._get_hierarchy_properties = get_hierarchy_properties
        self._get_dependency_properties = get_dependency_properties
        self._additional_hierarchies = additional_hierarchies
        self._legend_elements = legend_elements

        if (
            self._additional_hierarchies is not None
            and not self._additional_hierarchies.relationships.isdisjoint(
                self._graph.hierarchy_graph().hierarchies()
            )
        ):
            msg = "Additional hierarchies must not overlap with graph hierarchies"
            raise ValueError(msg)

        self._additional_dependencies = additional_dependencies

        if (
            self._additional_dependencies is not None
            and not self._additional_dependencies.relationships.isdisjoint(
                self._graph.dependency_graph().dependencies()
            )
        ):
            msg = "Additional dependencies must not overlap with graph dependencies"
            raise ValueError(msg)

        self._on_node_left_click = on_node_left_click

        mpl.use("Agg")
        self._fig = plt.figure()

        # Stops the network flipping upside down when you're spinning it
        mpl.rcParams["axes3d.mouserotationstyle"] = "azel"

        # An Axes3D is the returned type when the projection argument is
        # specified as "3d", hence the type ignore
        self._ax: mplot3d.Axes3D = self._fig.add_subplot(projection="3d")  # type: ignore[reportAttributeAccessIssue]
        self._fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        self._canvas = backend_tkagg.FigureCanvasTkAgg(self._fig, self)
        self._canvas.get_tk_widget().grid()
        self._annotation = text.Annotation("", (0, 0))
        self._motion_notify_event_callback_id: int | None = None
        self._button_release_event_callback_id: int | None = None

        self._task_collections = list[tuple[tasks.UID, art3d.Poly3DCollection]]()

        self._update_figure()

    def update_graph(
        self,
        graph: tasks.IUnconstrainedNetworkGraphView | None = None,
        get_task_annotation_text: Callable[[tasks.UID], str | None] | None = None,
        get_task_properties: Callable[[tasks.UID], NetworkTaskDrawingProperties]
        | None = None,
        get_hierarchy_properties: Callable[
            [tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties
        ]
        | None = None,
        get_dependency_properties: Callable[
            [tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties
        ]
        | None = None,
        additional_hierarchies: AdditionalRelationships
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        additional_dependencies: AdditionalRelationships
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        on_node_left_click: Callable[[tasks.UID], None]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
        legend_elements: Sequence[
            tuple[
                str, NetworkTaskDrawingProperties | NetworkRelationshipDrawingProperties
            ]
        ]
        | None
        | DefaultSentinel = DefaultSentinel.DEFAULT,
    ) -> None:
        if graph is not None:
            self._graph = graph

        if get_task_annotation_text is not None:
            self._get_task_annotation_text = get_task_annotation_text

        if get_task_properties is not None:
            self._get_task_properties = get_task_properties

        if get_hierarchy_properties is not None:
            self._get_hierarchy_properties = get_hierarchy_properties

        if get_dependency_properties is not None:
            self._get_dependency_properties = get_dependency_properties

        if additional_hierarchies is not DefaultSentinel.DEFAULT:
            self._additional_hierarchies = additional_hierarchies

            if (
                self._additional_hierarchies is not None
                and not self._additional_hierarchies.relationships.isdisjoint(
                    self._graph.hierarchy_graph().hierarchies()
                )
            ):
                msg = "Additional hierarchies must not overlap with graph hierarchies"
                raise ValueError(msg)

        if additional_dependencies is not DefaultSentinel.DEFAULT:
            self._additional_dependencies = additional_dependencies

            if (
                self._additional_dependencies is not None
                and not self._additional_dependencies.relationships.isdisjoint(
                    self._graph.dependency_graph().dependencies()
                )
            ):
                msg = "Additional dependencies must not overlap with graph dependencies"
                raise ValueError(msg)

        if on_node_left_click is not DefaultSentinel.DEFAULT:
            self._on_node_left_click = on_node_left_click

        if legend_elements is not DefaultSentinel.DEFAULT:
            self._legend_elements = legend_elements

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

        task_positions = (
            task_network_graph_drawing.calculate_task_positions_unnamed_method(
                graph=self._graph,
                task_cylinder_radius=_TASK_CYLINDER_RADIUS,
            )
        )
        self._task_positions = {
            task: XAxisCylinderPosition(
                x_min=position.min_dependency,
                x_max=position.max_dependency,
                y=position.depth,
                z=position.hierarchy,
            )
            for task, position in task_positions.items()
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

            task_cylinder_properties = CylinderDrawingProperties(
                colour=properties.colour,
                edge_colour=properties.edge_colour,
                number_of_polygons=_TASK_CYLINDER_NUMBER_OF_POLYGONS,
                alpha=properties.alpha,
            )

            label_text = str(task)

            label_properties = CylinderLabelDrawingProperties(
                colour=properties.label_colour, alpha=properties.label_alpha
            )

            collection = plot_x_axis_cylinder(
                ax=self._ax,
                radius=_TASK_CYLINDER_RADIUS,
                position=position,
                properties=task_cylinder_properties,
                label=CylinderLabel(text=label_text, properties=label_properties),
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

            properties = self._get_hierarchy_properties(supertask, subtask)

            arrow = Arrow3D(
                [arrow_x, arrow_x],
                [arrow_source_y, arrow_target_y],
                [arrow_source_z, arrow_target_z],
                mutation_scale=10,
                color=str(properties.colour),
                alpha=float(properties.alpha),
                linestyle=str(properties.line_style),
                connectionstyle=str(properties.connection_style),
                arrowstyle=str(properties.arrow_style),
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

            arrow = Arrow3D(
                [arrow_source_x, arrow_target_x],
                [arrow_source_y, arrow_target_y],
                [arrow_source_z, arrow_target_z],
                mutation_scale=10,
                color=str(properties.colour),
                alpha=float(properties.alpha),
                linestyle=str(properties.line_style),
                connectionstyle=str(properties.connection_style),
                arrowstyle=str(properties.arrow_style),
            )
            self._ax.add_artist(arrow)

    def _update_additional_hierarchy_arrows(self) -> None:
        assert self._task_positions is not None

        if self._additional_hierarchies is None:
            return

        for supertask, subtask in self._additional_hierarchies.relationships:
            supertask_position = self._task_positions[supertask]
            arrow_source_x = supertask_position.x_center
            arrow_source_y = supertask_position.y
            arrow_source_z = supertask_position.z

            subtask_position = self._task_positions[subtask]
            arrow_target_x = subtask_position.x_center
            arrow_target_y = subtask_position.y
            arrow_target_z = subtask_position.z

            properties = self._additional_hierarchies.get_relationship_properties(
                supertask, subtask
            )

            arrow = Arrow3D(
                [arrow_source_x, arrow_target_x],
                [arrow_source_y, arrow_target_y],
                [arrow_source_z, arrow_target_z],
                mutation_scale=10,
                color=str(properties.colour),
                alpha=float(properties.alpha),
                linestyle=str(properties.line_style),
                connectionstyle=str(properties.connection_style),
                arrowstyle=str(properties.arrow_style),
            )

            self._ax.add_artist(arrow)

    def _update_additional_dependency_arrows(self) -> None:
        assert self._task_positions is not None

        if self._additional_dependencies is None:
            return

        for (
            dependee_task,
            dependent_task,
        ) in self._additional_dependencies.relationships:
            dependee_task_position = self._task_positions[dependee_task]
            arrow_source_x = dependee_task_position.x_max
            arrow_source_y = dependee_task_position.y
            arrow_source_z = dependee_task_position.z

            dependent_task_position = self._task_positions[dependent_task]
            arrow_target_x = dependent_task_position.x_min
            arrow_target_y = dependent_task_position.y
            arrow_target_z = dependent_task_position.z

            properties = self._additional_dependencies.get_relationship_properties(
                dependee_task, dependent_task
            )

            arrow = Arrow3D(
                [arrow_source_x, arrow_target_x],
                [arrow_source_y, arrow_target_y],
                [arrow_source_z, arrow_target_z],
                mutation_scale=10,
                color=str(properties.colour),
                alpha=float(properties.alpha),
                linestyle=str(properties.line_style),
                connectionstyle=str(properties.connection_style),
                arrowstyle=str(properties.arrow_style),
            )
            self._ax.add_artist(arrow)

    def _update_legend(self) -> None:
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

        if self._legend_elements is None:
            return

        legend_elements = list[Patch | FancyArrowPatch]()

        for label, element in self._legend_elements:
            if isinstance(element, NetworkTaskDrawingProperties):
                patch = Patch(
                    facecolor=str(element.colour),
                    edgecolor=str(element.edge_colour),
                    alpha=float(element.alpha),
                    label=label,
                )
            else:
                patch = FancyArrowPatch(
                    (0, 3),
                    (22, 3),
                    linestyle=str(element.line_style),
                    arrowstyle=ArrowStyle.Simple(
                        head_length=0.3,
                        head_width=0.3,
                        tail_width=0.05,
                    ),  # pyright: ignore[reportCallIssue]
                    color=str(element.colour),
                    alpha=float(element.alpha),
                    label=label,
                    mutation_scale=20,
                )
            legend_elements.append(patch)

        self._ax.legend(
            handles=legend_elements,
            handler_map={FancyArrowPatch: ArrowHandler()},
            loc="upper right",
        )

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
                y_min = min(y_min, task_position.y - float(_TASK_CYLINDER_RADIUS))
                y_max = max(y_max, task_position.y + float(_TASK_CYLINDER_RADIUS))
                z_min = min(z_min, task_position.z - float(_TASK_CYLINDER_RADIUS))
                z_max = max(z_max, task_position.z + float(_TASK_CYLINDER_RADIUS))

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
            color=str(_AXIS_ARROW_COLOUR),
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
            color=str(_AXIS_ARROW_COLOUR),
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
