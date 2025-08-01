import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.presentation.tkinter_gui.tabs.dependency_panel.creation_deletion_panel.dependency_deletion_window import (
    DependencyDeletionWindow,
)


class DependencyDeletionButton(ttk.Button):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(
            master=master,
            text="Delete Dependency",
            command=lambda: DependencyDeletionWindow(
                master=self,
                dependency_options=logic_layer.get_task_system()
                .network_graph()
                .dependency_graph()
                .dependencies(),
                delete_dependency=logic_layer.delete_task_dependency,
                get_task_name=lambda task: logic_layer.get_task_system()
                .attributes_register()[task]
                .name,
            ),
        )
