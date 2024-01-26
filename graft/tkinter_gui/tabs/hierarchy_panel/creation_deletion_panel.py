import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.tkinter_gui.tabs.hierarchy_panel.hierarchy_creation_button import (
    HierarchyCreationButton,
)
from graft.tkinter_gui.tabs.hierarchy_panel.hierarchy_deletion_button import (
    HierarchyDeletionButton,
)


class CreationDeletionPanel(ttk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self.logic_layer = logic_layer

        self.hierarchy_creation_button = HierarchyCreationButton(
            self, logic_layer=self.logic_layer
        )
        self.hierarchy_deletion_button = HierarchyDeletionButton(
            self, logic_layer=self.logic_layer
        )

        self.hierarchy_creation_button.grid(row=0, column=0)
        self.hierarchy_deletion_button.grid(row=0, column=1)
