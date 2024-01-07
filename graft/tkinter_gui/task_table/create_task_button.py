import functools
import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.tkinter_gui.task_table.task_creation_window import (
    create_task_creation_window,
)


class CreateTaskButton(ttk.Button):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        self.logic_layer = logic_layer
        super().__init__(master, text="Create Task", command=functools.partial(
            create_task_creation_window, master=self, logic_layer=self.logic_layer
        ))
