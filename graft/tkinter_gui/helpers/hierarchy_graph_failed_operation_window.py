import tkinter as tk
from collections.abc import Collection, Container
from tkinter import ttk

from graft.domain import tasks
from graft.tkinter_gui.helpers.failed_operation_window import OperationFailedWindow
from graft.tkinter_gui.helpers.hierarchy_graph import HierarchyGraph


class HierarchyGraphOperationFailedWindow(OperationFailedWindow):
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

        self.graph = HierarchyGraph(
            master=self,
            system=system,
            highlighted_tasks=highlighted_tasks,
            additional_hierarchies=additional_hierarchies,
        )

        self.label.grid(row=0, column=0)
        self.graph.grid(row=1, column=0)
