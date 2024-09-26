import functools
import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.presentation.tkinter_gui.tabs.hierarchy_panel.creation_deletion_panel.hierarchy_creation_window import (
    HierarchyCreationWindow,
)


class HierarchyCreationButton(ttk.Button):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        self.logic_layer = logic_layer
        super().__init__(
            master,
            text="Create Hierarchy",
            command=functools.partial(
                HierarchyCreationWindow,
                master=self,
                logic_layer=self.logic_layer,
            ),
        )
