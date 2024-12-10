import numpy as np
from matplotlib import patches
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import art3d

from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.radius import (
    Radius,
)

from .cylinder_drawing_properties import CylinderDrawingProperties
from .cylinder_label import CylinderLabel
from .cylinder_position import XAxisCylinderPosition


def plot_x_axis_cylinder(
    ax: mplot3d.Axes3D,
    radius: Radius,
    position: XAxisCylinderPosition,
    properties: CylinderDrawingProperties,
    label: CylinderLabel | None = None,
) -> art3d.Poly3DCollection:
    xs = np.array([position.x_min, position.x_max])
    thetas = np.linspace(0, 2 * np.pi, properties.number_of_polygons)

    XS, THETAS = np.meshgrid(xs, thetas)

    YS = position.y + float(radius) * np.sin(THETAS)
    ZS = position.z + float(radius) * np.cos(THETAS)

    collection: art3d.Poly3DCollection = ax.plot_surface(
        XS, YS, ZS, color=str(properties.colour), alpha=float(properties.alpha)
    )

    if label is not None:
        ax.text(
            position.x_center,
            position.y,
            position.z,
            label.text,
            color=str(label.properties.colour),
            alpha=float(label.properties.alpha),
            zorder=100,  # set to 100 to ensure that labels are always drawn on top of the cylinders, and therefore visible
        )

    # Plot the end-caps of the cylinder
    for x in [position.x_min, position.x_max]:
        circle = patches.Circle(
            xy=(position.y, position.z),
            radius=float(radius),
            facecolor=str(properties.colour),
            edgecolor=str(properties.edge_colour),
            alpha=float(properties.alpha),
        )
        ax.add_patch(circle)
        # This method actually handles float values for z just fine, hence the type ignore
        art3d.pathpatch_2d_to_3d(circle, z=x, zdir="x")  # type: ignore[reportArgumentType]

    return collection
