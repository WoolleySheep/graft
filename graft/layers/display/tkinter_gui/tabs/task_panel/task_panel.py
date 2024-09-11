import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.display.tkinter_gui.tabs.task_panel.creation_deletion_panel import (
    CreationDeletionPanel,
)
from graft.layers.display.tkinter_gui.tabs.task_panel.task_table import TaskTable


class TaskPanel(ttk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self.logic_layer = logic_layer

        self.creation_deletion_panel = CreationDeletionPanel(
            self, logic_layer=self.logic_layer
        )
        self.task_tree_view = TaskTable(self, logic_layer=self.logic_layer)

        self.creation_deletion_panel.grid(row=0, column=0)
        self.task_tree_view.grid(row=1, column=0)
