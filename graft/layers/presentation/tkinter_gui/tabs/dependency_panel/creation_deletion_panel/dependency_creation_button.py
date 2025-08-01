import functools
import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.tabs.dependency_panel.creation_deletion_panel.dependency_creation_window import (
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
                get_tasks=lambda: self.logic_layer.get_task_system().tasks(),
                get_incomplete_tasks=lambda: tasks.get_incomplete_system(
                    self.logic_layer.get_task_system()
                ).tasks(),
                get_task_name=lambda task: self.logic_layer.get_task_system()
                .attributes_register()[task]
                .name,
                create_dependency=lambda dependee_task,
                dependent_task: self.logic_layer.create_task_hierarchy(
                    dependee_task, dependent_task
                ),
            ),
        )
