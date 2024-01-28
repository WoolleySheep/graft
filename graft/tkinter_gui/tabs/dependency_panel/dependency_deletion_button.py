import functools
import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.tkinter_gui.tabs.dependency_panel.dependency_deletion_window import (
    create_dependency_deletion_window,
)


class DependencyDeletionButton(ttk.Button):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        self.logic_layer = logic_layer
        super().__init__(
            master,
            text="Delete Dependency",
            command=functools.partial(
                create_dependency_deletion_window,
                master=self,
                logic_layer=self.logic_layer,
            ),
        )
