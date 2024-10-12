import dataclasses

import matplotlib as mpl
import numpy as np
from matplotlib import backend_bases as mpl_backend_bases
from matplotlib import patches
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import art3d


@dataclasses.dataclass(frozen=True)
class LabelDrawingProperties:
    colour: str = "black"
    alpha: int = 1

    def __post__init__(self) -> None:
        if not (0 < self.alpha <= 1):
            raise ValueError("Alpha must be in range (0, 1].")

@dataclasses.dataclass(frozen=True)
class Label:
    text: str
    properties: LabelDrawingProperties


@dataclasses.dataclass(frozen=True)
class CylinderDimensions:
    radius: float
    x_start: int
    x_stop: int
    y: float = 0
    z: float = 0

    @property
    def x_center(self) -> float:
        return (self.x_start + self.x_stop) / 2

@dataclasses.dataclass(frozen=True)
class CylinderDrawingProperties:
    resolution: int = 10
    colour: str = "blue"
    alpha: int = 1

    def __post_init__(self) -> None:
        if self.resolution < 3:
            raise ValueError("Resolution must be at least 3.")
        if not (0 < self.alpha <= 1):
            raise ValueError("Alpha must be in range (0, 1].")


named_collections = list[tuple[str, art3d.Poly3DCollection]]()

def _on_motion_notify_event(event: mpl_backend_bases.Event) -> None:
        if not isinstance(event, mpl_backend_bases.MouseEvent):
            raise TypeError

        if event.name != "motion_notify_event":
            raise ValueError
        
        global named_collections
        for name, collection in named_collections:
            if collection.contains(event)[0]:
                print(f"Mouse over {name}")


def main() -> None:
    fig = plt.figure()
    ax: mplot3d.Axes3D = fig.add_subplot(projection="3d")
    global named_collections

    named_collections.append(("1", plot_x_axis_cylinder(ax=ax, dimensions=CylinderDimensions(radius=0.1, x_start=0, x_stop=1), properties=CylinderDrawingProperties(), label=Label(text="1", properties=LabelDrawingProperties()))))
    named_collections.append(("2", plot_x_axis_cylinder(ax=ax, dimensions=CylinderDimensions(radius=0.1, x_start=0, x_stop=1, y=4), properties=CylinderDrawingProperties(), label=Label(text="2", properties=LabelDrawingProperties()))))

    fig.canvas.mpl_connect("motion_notify_event", _on_motion_notify_event)

    ax.grid(False)

    for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
        axis.set_ticks([])
        axis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        axis.line.set_color((1.0, 1.0, 1.0, 0.0))
        axis._axinfo["grid"]["color"] = (1, 1, 1, 0)

    ax.set_aspect('equal')

    plt.show()

def plot_x_axis_cylinder(ax: mplot3d.Axes3D, dimensions: CylinderDimensions, properties: CylinderDrawingProperties, label: Label | None = None) -> art3d.Poly3DCollection:
    """https://stackoverflow.com/questions/39822480/plotting-a-solid-cylinder-centered-on-a-plane-in-matplotlib"""

    xs = np.array([dimensions.x_start, dimensions.x_stop])
    thetas = np.linspace(0, 2 * np.pi, properties.resolution)

    XS, THETAS = np.meshgrid(xs, thetas)

    YS = dimensions.y + dimensions.radius * np.sin(THETAS)
    ZS = dimensions.z + dimensions.radius * np.cos(THETAS)

    collection: art3d.Poly3DCollection = ax.plot_surface(XS, YS, ZS, color=properties.colour, alpha=properties.alpha)

    if label is not None:
        ax.text(dimensions.x_center, dimensions.y, dimensions.z, label.text, color=label.properties.colour, alpha=label.properties.alpha, zorder=10)

    for x in [dimensions.x_start, dimensions.x_stop]:
        circle = patches.Circle(xy=(dimensions.y, dimensions.z), radius=dimensions.radius, color=properties.colour, alpha=0.5)
        ax.add_patch(circle)
        art3d.pathpatch_2d_to_3d(circle, z=x, zdir="x")

    return collection


    

main()