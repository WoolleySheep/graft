import functools
import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.display.tkinter_gui.tabs.dependency_panel.dependency_creation_window import (
    DependencyCreationWindow,
)


class DependencyCreationButton(ttk.Button):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        self.logic_layer = logic_layer
        super().__init__(
            master,
            text="Create Dependency",
            command=functools.partial(
                DependencyCreationWindow,
                master=self,
                logic_layer=self.logic_layer,
            ),
        )
