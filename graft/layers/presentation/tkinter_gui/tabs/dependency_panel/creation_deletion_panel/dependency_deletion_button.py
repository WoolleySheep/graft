import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.presentation.tkinter_gui.tabs.dependency_panel.creation_deletion_panel.dependency_deletion_window import (
    DependencyDeletionWindow,
)


class DependencyDeletionButton(ttk.Button):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(
            master,
            text="Delete Dependency",
            command=lambda: DependencyDeletionWindow(
                master=self, logic_layer=logic_layer
            ),
        )
