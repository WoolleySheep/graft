import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.presentation.tkinter_gui.tabs.task_panel.task_creation_window import (
    TaskCreationWindow,
)


class TaskCreationButton(ttk.Button):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(
            master,
            text="Create Task",
            command=lambda: TaskCreationWindow(master=self, logic_layer=logic_layer),
        )
