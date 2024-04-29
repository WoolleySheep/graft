import tkinter as tk
from collections.abc import Collection, Container
from tkinter import ttk

from graft.domain import tasks
from graft.tkinter_gui.helpers.dependency_graph import DependencyGraph
from graft.tkinter_gui.helpers.failed_operation_window import OperationFailedWindow


class DependencyGraphOperationFailedWindow(OperationFailedWindow):
    def __init__(
        self,
        master: tk.Misc,
        text: str,
        system: tasks.System,
        highlighted_tasks: Container[tasks.UID] | None = None,
        highlighted_dependencies: Container[tuple[tasks.UID, tasks.UID]] | None = None,
        additional_dependencies: Collection[tuple[tasks.UID, tasks.UID]] | None = None,
    ) -> None:
        super().__init__(master=master)

        self.label = ttk.Label(self, text=text)

        self.graph = DependencyGraph(
            master=self,
            system=system,
            highlighted_tasks=highlighted_tasks,
            highlighted_dependencies=highlighted_dependencies,
            additional_dependencies=additional_dependencies,
        )

        self.label.grid(row=0, column=0)
        self.graph.grid(row=1, column=0)
