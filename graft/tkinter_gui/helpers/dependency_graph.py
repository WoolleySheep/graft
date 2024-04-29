import tkinter as tk
from collections.abc import Collection, Container

from graft.domain import tasks
from graft.tkinter_gui.helpers.system_graph import GraphType, SystemGraph


class DependencyGraph(SystemGraph):
    """tkinter frame showing a Dependency graph."""

    def __init__(
        self,
        master: tk.Misc,
        system: tasks.System,
        highlighted_tasks: Container[tasks.UID] | None = None,
        additional_dependencies: Collection[tuple[tasks.UID, tasks.UID]] | None = None,
    ) -> None:
        super().__init__(
            master=master,
            graph_type=GraphType.DEPENDENCY,
            system=system,
            highlighted_tasks=highlighted_tasks,
            additional_edges=additional_dependencies,
        )
