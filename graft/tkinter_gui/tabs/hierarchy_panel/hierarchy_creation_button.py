import functools
import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.tkinter_gui.tabs.hierarchy_panel.hierarchy_creation_window import (
    create_hierarchy_creation_window,
)


class HierarchyCreationButton(ttk.Button):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        self.logic_layer = logic_layer
        super().__init__(
            master,
            text="Create Hierarchy",
            command=functools.partial(
                create_hierarchy_creation_window,
                master=self,
                logic_layer=self.logic_layer,
            ),
        )
