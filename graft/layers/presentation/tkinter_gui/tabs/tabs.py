import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.presentation.tkinter_gui.tabs.dependency_panel import DependencyPanel
from graft.layers.presentation.tkinter_gui.tabs.hierarchy_panel import HierarchyPanel
from graft.layers.presentation.tkinter_gui.tabs.importance_panel import ImportancePanel
from graft.layers.presentation.tkinter_gui.tabs.network_panel import NetworkPanel
from graft.layers.presentation.tkinter_gui.tabs.priority_table import PriorityTable
from graft.layers.presentation.tkinter_gui.tabs.progress_board import ProgressBoard
from graft.layers.presentation.tkinter_gui.tabs.search_panel import SearchPanel
from graft.layers.presentation.tkinter_gui.tabs.task_panel import TaskPanel


class Tabs(ttk.Notebook):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)

        self._task_panel = TaskPanel(self, logic_layer)
        self._hierarchy_panel = HierarchyPanel(self, logic_layer)
        self._dependency_panel = DependencyPanel(self, logic_layer)
        self._network_panel = NetworkPanel(self, logic_layer)
        self._importance_panel = ImportancePanel(self, logic_layer)
        self._progress_board = ProgressBoard(self, logic_layer)
        self._priority_table = PriorityTable(self, logic_layer)
        self._search_panel = SearchPanel(self, logic_layer)

        self.add(self._task_panel, text="Tasks")
        self.add(self._hierarchy_panel, text="Hierarchies")
        self.add(self._dependency_panel, text="Dependencies")
        self.add(self._network_panel, text="Network")
        self.add(self._importance_panel, text="Importance")
        self.add(self._progress_board, text="Progress")
        self.add(self._priority_table, text="Priorities")
        self.add(self._search_panel, text="Search")
