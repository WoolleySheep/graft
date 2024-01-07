import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.tkinter_gui.tabs.hierarchy_graph import HierarchyGraph
from graft.tkinter_gui.tabs.task_panel import TaskPanel


class Tabs(ttk.Notebook):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self.logic_layer = logic_layer

        self.task_panel = TaskPanel(self, logic_layer)
        self.hierarchy_panel = HierarchyGraph(self, logic_layer)

        self.add(self.task_panel, text="Task Table")
        self.add(self.hierarchy_panel, text="Hierarchy Graph")