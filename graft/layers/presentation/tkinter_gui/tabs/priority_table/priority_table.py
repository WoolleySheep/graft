import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.presentation.tkinter_gui.tabs.priority_table.priority_tree_view import (
    PriorityTreeView,
)


class PriorityTable(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master)
        self.logic_layer = logic_layer

        self.priority_tree_view = PriorityTreeView(self, logic_layer=self.logic_layer)

        # Create a Scrollbar
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.priority_tree_view.yview
        )

        # Configure the Treeview to use the scrollbar
        self.priority_tree_view.configure(yscrollcommand=self.scrollbar.set)

        self.priority_tree_view.grid(row=0, column=0)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        # Place the scrollbar on the right side of the Treeview
