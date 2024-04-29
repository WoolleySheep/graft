import tkinter as tk
from collections.abc import Collection, Container, Set
from tkinter import ttk

from graft.domain import tasks
from graft.tkinter_gui.helpers import failed_operation_window, hierarchy_graph


class SingleHierarchyGraphOperationFailedWindow(
    failed_operation_window.OperationFailedWindow
):
    def __init__(
        self,
        master: tk.Misc,
        text: str,
        system: tasks.System,
        highlighted_tasks: Container[tasks.UID] | None = None,
        additional_hierarchies: Collection[tuple[tasks.UID, tasks.UID]] | None = None,
    ) -> None:
        super().__init__(master=master)

        self.label = ttk.Label(self, text=text)

        self.graph = hierarchy_graph.HierarchyGraph(
            master=self,
            system=system,
            highlighted_tasks=highlighted_tasks,
            additional_hierarchies=additional_hierarchies,
        )

        self.label.grid(row=0, column=0)
        self.graph.grid(row=1, column=0)
