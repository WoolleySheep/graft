import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.presentation.tkinter_gui.tabs.progress_panel.progress_board import (
    ProgressBoard,
)
from graft.layers.presentation.tkinter_gui.tabs.progress_panel.progress_graph import (
    ProgressGraph,
)


class ProgressPanel(ttk.Notebook):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)

        self._graph = ProgressGraph(self, logic_layer)
        self._board = ProgressBoard(self, logic_layer)

        self.add(self._graph, text="Graph")
        self.add(self._board, text="Board")
