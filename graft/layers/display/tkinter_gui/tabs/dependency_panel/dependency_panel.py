import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.display.tkinter_gui.tabs.dependency_panel.creation_deletion_panel import (
    CreationDeletionPanel,
)
from graft.layers.display.tkinter_gui.tabs.dependency_panel.dependency_graph import (
    DependencyGraph,
)


class DependencyPanel(ttk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self.logic_layer = logic_layer

        self.creation_deletion_panel = CreationDeletionPanel(
            self, logic_layer=self.logic_layer
        )
        self.dependency_graph = DependencyGraph(self, logic_layer=self.logic_layer)

        self.creation_deletion_panel.grid(row=0, column=0)
        self.dependency_graph.grid(row=1, column=0)
