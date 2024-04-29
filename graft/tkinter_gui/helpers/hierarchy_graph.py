import tkinter as tk
from collections.abc import Collection, Container

from graft.domain import tasks
from graft.tkinter_gui.helpers.system_graph import GraphType, SystemGraph


class HierarchyGraph(SystemGraph):
    """tkinter frame showing a Hierarchy graph."""

    def __init__(
        self,
        master: tk.Misc,
        system: tasks.System,
        highlighted_tasks: Container[tasks.UID] | None = None,
        highlighted_hierarchies: Container[tuple[tasks.UID, tasks.UID]] | None = None,
        additional_hierarchies: Collection[tuple[tasks.UID, tasks.UID]] | None = None,
    ) -> None:
        super().__init__(
            master=master,
            graph_type=GraphType.HIERARCHY,
            system=system,
            highlighted_tasks=highlighted_tasks,
            highlighted_edges=highlighted_hierarchies,
            additional_edges=additional_hierarchies,
        )
