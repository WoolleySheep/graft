import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.display.tkinter_gui.tabs.task_panel.task_deletion_window import (
    TaskDeletionWindow,
)


class TaskDeletionButton(ttk.Button):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        self.logic_layer = logic_layer
        super().__init__(
            master,
            text="Delete Task",
            command=lambda: TaskDeletionWindow(master=self, logic_layer=logic_layer),
        )
