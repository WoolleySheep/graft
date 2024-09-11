import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.presentation.tkinter_gui.tabs.task_panel.task_creation_button import (
    TaskCreationButton,
)
from graft.layers.presentation.tkinter_gui.tabs.task_panel.task_deletion_button import (
    TaskDeletionButton,
)


class CreationDeletionPanel(ttk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self.logic_layer = logic_layer

        self.task_creation_button = TaskCreationButton(
            self, logic_layer=self.logic_layer
        )
        self.task_deletion_button = TaskDeletionButton(
            self, logic_layer=self.logic_layer
        )

        self.task_creation_button.grid(row=0, column=0)
        self.task_deletion_button.grid(row=0, column=1)
