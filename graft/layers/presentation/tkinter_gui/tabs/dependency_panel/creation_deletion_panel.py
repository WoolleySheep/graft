import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.presentation.tkinter_gui.tabs.dependency_panel.dependency_creation_button import (
    DependencyCreationButton,
)
from graft.layers.presentation.tkinter_gui.tabs.dependency_panel.dependency_deletion_button import (
    DependencyDeletionButton,
)


class CreationDeletionPanel(ttk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self.logic_layer = logic_layer

        self.dependency_creation_button = DependencyCreationButton(
            self, logic_layer=logic_layer
        )
        self.dependency_deletion_button = DependencyDeletionButton(
            self, logic_layer=logic_layer
        )

        self.dependency_creation_button.grid(row=0, column=0)
        self.dependency_deletion_button.grid(row=0, column=1)
