import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.presentation.tkinter_gui.tabs.hierarchy_panel.creation_deletion_panel.hierarchy_deletion_window import (
    HierarchyDeletionWindow,
)


class HierarchyDeletionButton(ttk.Button):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(
            master=master,
            text="Delete Hierarchy",
            command=lambda: HierarchyDeletionWindow(
                master=self,
                hierarchy_options=sorted(
                    logic_layer.get_task_system()
                    .network_graph()
                    .hierarchy_graph()
                    .hierarchies()
                ),
                delete_hierarchy=logic_layer.delete_task_hierarchy,
                get_task_name=lambda task: logic_layer.get_task_system()
                .attributes_register()[task]
                .name,
            ),
        )
