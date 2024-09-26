import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk

import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.backends import backend_tkagg

from graft import architecture
from graft.domain import tasks
from graft.domain.tasks.network_graph import NetworkGraph


@dataclass(frozen=True)
class Coordinate3D:
    x: float
    y: float
    z: float


class NetworkPanel(ttk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        mpl.use("Agg")
        self._logic_layer = logic_layer
        self._fig = plt.figure()
        self._ax = self._fig.add_subplot(projection="3d")
        self._canvas = backend_tkagg.FigureCanvasTkAgg(self._fig, self)
        self._canvas.get_tk_widget().grid()

        # Hardcoded graph graph
        graph = NetworkGraph.empty()
        graph.add_task(tasks.UID(0))
        graph.add_task(tasks.UID(1))
        graph.add_task(tasks.UID(2))
        graph.add_hierarchy(tasks.UID(0), tasks.UID(1))
        graph.add_hierarchy(tasks.UID(0), tasks.UID(2))
        graph.add_dependency(tasks.UID(1), tasks.UID(2))

        # Hardcoded node positions
        positions = {
            tasks.UID(0): Coordinate3D(0, 0, 1),
            tasks.UID(1): Coordinate3D(0, 0, 0),
            tasks.UID(2): Coordinate3D(1, 0, 0),
        }

        # Draw fancy graph

        # TODOs
        #   - Replace lines with arrows
        #   - Increase node sizing
        #   - Show node number on/near nodes
        #   - Show node name when hover over
        #   - Autogenerate node positions from network graph

        # Later TODOs
        #   - Make nodes clickable

        nodes = list[tasks.UID]()
        xs = list[float]()
        ys = list[float]()
        zs = list[float]()
        for task, coordinate in positions.items():
            nodes.append(task)
            xs.append(coordinate.x)
            ys.append(coordinate.y)
            zs.append(coordinate.z)

        self._ax.scatter(xs, ys, zs)

        for supertask, subtask in graph.hierarchy_graph().hierarchies():
            supertask_position = positions[supertask]
            subtask_position = positions[subtask]
            self._ax.plot(
                [supertask_position.x, subtask_position.x],
                [supertask_position.y, subtask_position.y],
                [supertask_position.z, subtask_position.z],
                color="black",
            )

        for dependee_task, dependent_task in graph.dependency_graph().dependencies():
            dependee_position = positions[dependee_task]
            dependent_position = positions[dependent_task]
            self._ax.plot(
                [dependee_position.x, dependent_position.x],
                [dependee_position.y, dependent_position.y],
                [dependee_position.z, dependent_position.z],
                color="red",
            )

        self._ax.grid(False)

        for axis in [self._ax.xaxis, self._ax.yaxis, self._ax.zaxis]:
            axis.set_ticks([])
            axis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            axis._axinfo["grid"]["color"] = (1, 1, 1, 0)
