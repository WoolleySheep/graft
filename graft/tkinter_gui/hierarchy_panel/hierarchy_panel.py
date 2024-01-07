import tkinter as tk

from graft import architecture
from graft.tkinter_gui.hierarchy_panel.hierarchy_graph_image import HierarchyGraphImage
from graft.tkinter_gui.hierarchy_panel.task_legend_table import TaskLegendTable


class HierarchyPanel(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master)
        self.logic_layer = logic_layer

        self.hierarchy_graph = HierarchyGraphImage(self, logic_layer)
        self.task_legend = TaskLegendTable(self, logic_layer)

        self.hierarchy_graph.grid(row=0, column=0)
        self.task_legend.grid(row=0, column=1)
