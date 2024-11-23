import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.presentation.tkinter_gui.tabs.importance_panel.importance_board import (
    ImportanceBoard,
)
from graft.layers.presentation.tkinter_gui.tabs.importance_panel.importance_graph import (
    ImportanceGraph,
)


class ImportancePanel(ttk.Notebook):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)

        self._graph = ImportanceGraph(self, logic_layer)
        self._table = ImportanceBoard(self, logic_layer)

        self.add(self._graph, text="Graph")
        self.add(self._table, text="Table")
