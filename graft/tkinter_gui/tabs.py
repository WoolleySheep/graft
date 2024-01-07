import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.tkinter_gui.task_table import TaskTable


class Tabs(ttk.Notebook):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self.logic_layer = logic_layer

        self.task_table = TaskTable(self, logic_layer)
        self.add(self.task_table, text="Task Table")
