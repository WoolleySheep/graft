import functools
import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.tkinter_gui.task_table.create_task_button import CreateTaskButton
from graft.tkinter_gui.task_table.task_tree_view import TaskTreeView


class TaskTable(ttk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self.logic_layer = logic_layer

        self.create_task_button = CreateTaskButton(self, logic_layer=self.logic_layer)
        self.task_tree_view = TaskTreeView(self, logic_layer=self.logic_layer)

        self.create_task_button.grid(row=0)
        self.task_tree_view.grid(row=1)

