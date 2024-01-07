import functools
import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.tkinter_gui.tabs.task_panel.create_task_button import CreateTaskButton
from graft.tkinter_gui.tabs.task_panel.task_table import TaskTable


class TaskPanel(ttk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self.logic_layer = logic_layer

        self.create_task_button = CreateTaskButton(self, logic_layer=self.logic_layer)
        self.task_tree_view = TaskTable(self, logic_layer=self.logic_layer)

        self.create_task_button.grid(row=0)
        self.task_tree_view.grid(row=1)
