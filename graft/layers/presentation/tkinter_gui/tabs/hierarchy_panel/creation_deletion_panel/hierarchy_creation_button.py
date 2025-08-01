import functools
import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
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
                get_tasks=lambda: self.logic_layer.get_task_system().tasks(),
                get_incomplete_tasks=lambda: tasks.get_incomplete_system(
                    self.logic_layer.get_task_system()
                ).tasks(),
                get_task_name=lambda task: self.logic_layer.get_task_system()
                .attributes_register()[task]
                .name,
                create_hierarchy=lambda supertask,
                subtask: self.logic_layer.create_task_hierarchy(supertask, subtask),
            ),
        )
