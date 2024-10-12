import dataclasses

import numpy as np
from matplotlib import patches
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import art3d

from graft.layers.presentation.tkinter_gui import task_network_graph_drawing


@dataclasses.dataclass(frozen=True)
class CylinderDrawingProperties:
    colour: str
    number_of_polygons: int = 10
    alpha: float = 1

    def __post_init__(self) -> None:
        if self.number_of_polygons < 3:
            msg = "Number of polygons must be at least 3 to form a closed volume."
            raise ValueError(
                msg
            )
        if not (0 < self.alpha <= 1):
            msg = "Alpha must be in range (0, 1]."
            raise ValueError(msg)


@dataclasses.dataclass(frozen=True)
class LabelDrawingProperties:
    colour: str
    alpha: float = 1

    def __post__init__(self) -> None:
        if not (0 < self.alpha <= 1):
            msg = "Alpha must be in range (0, 1]."
            raise ValueError(msg)


@dataclasses.dataclass(frozen=True)
class Label:
    text: str
    properties: LabelDrawingProperties


def plot_x_axis_cylinder(
    ax: mplot3d.Axes3D,
    radius: float,
    position: task_network_graph_drawing.XAxisCylinderPosition,
    properties: CylinderDrawingProperties,
    label: Label | None = None,
) -> art3d.Poly3DCollection:
    if radius <= 0:
        msg = "Radius must be positive."
        raise ValueError(msg)

    xs = np.array([position.x_min, position.x_max])
    thetas = np.linspace(0, 2 * np.pi, properties.number_of_polygons)

    XS, THETAS = np.meshgrid(xs, thetas)

    YS = position.y + radius * np.sin(THETAS)
    ZS = position.z + radius * np.cos(THETAS)

    collection: art3d.Poly3DCollection = ax.plot_surface(
        XS, YS, ZS, color=properties.colour, alpha=properties.alpha
    )

    # z order set to 10 to ensure that labels are always drawn on top of the cylinders, and therefore visible
    if label is not None:
        ax.text(
            position.x_center,
            position.y,
            position.z,
            label.text,
            color=label.properties.colour,
            alpha=label.properties.alpha,
            zorder=10,
        )

    # Plot the end-caps of the cylinder
    for x in [position.x_min, position.x_max]:
        circle = patches.Circle(
            xy=(position.y, position.z),
            radius=radius,
            color=properties.colour,
            alpha=properties.alpha,
        )
        ax.add_patch(circle)
        # This method actually handles float values for z just fine, hence the type ignore
        art3d.pathpatch_2d_to_3d(circle, z=x, zdir="x") # type: ignore[reportArgumentType]

    return collection
