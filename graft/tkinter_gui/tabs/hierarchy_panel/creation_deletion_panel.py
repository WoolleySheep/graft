import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.tkinter_gui.tabs.hierarchy_panel.hierarchy_creation_button import (
    HierarchyCreationButton,
)


class CreationDeletionPanel(ttk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self.logic_layer = logic_layer

        self.hierarchy_creation_button = HierarchyCreationButton(
            self, logic_layer=self.logic_layer
        )

        self.hierarchy_creation_button.grid(column=0)
