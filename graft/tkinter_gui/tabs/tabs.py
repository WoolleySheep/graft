import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.tkinter_gui.tabs.dependency_panel import DependencyPanel
from graft.tkinter_gui.tabs.hierarchy_panel import HierarchyPanel
from graft.tkinter_gui.tabs.priority_table import PriorityTable
from graft.tkinter_gui.tabs.task_panel import TaskPanel


class Tabs(ttk.Notebook):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self.logic_layer = logic_layer

        self.task_panel = TaskPanel(self, logic_layer)
        self.hierarchy_panel = HierarchyPanel(self, logic_layer)
        self.dependency_panel = DependencyPanel(self, logic_layer)
        self.priority_table = PriorityTable(self, logic_layer)

        self.add(self.task_panel, text="Task Table")
        self.add(self.hierarchy_panel, text="Hierarchy Panel")
        self.add(self.dependency_panel, text="Dependency Panel")
        self.add(self.priority_table, text="Priority Table")
