import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.presentation.tkinter_gui.tabs.hierarchy_panel.creation_deletion_panel import (
    CreationDeletionPanel,
)
from graft.layers.presentation.tkinter_gui.tabs.hierarchy_panel.hierarchy_graph import (
    HierarchyGraph,
)


class HierarchyPanel(ttk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self.logic_layer = logic_layer

        self.creation_deletion_panel = CreationDeletionPanel(
            self, logic_layer=self.logic_layer
        )
        self.hierarchy_graph = HierarchyGraph(self, logic_layer=self.logic_layer)

        self.creation_deletion_panel.grid(row=0, column=0)
        self.hierarchy_graph.grid(row=1, column=0)
