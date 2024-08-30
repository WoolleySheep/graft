import tkinter as tk

from graft import architecture
from graft.tkinter_gui.tabs.tabs import Tabs
from graft.tkinter_gui.task_details import TaskDetails


class GUI(tk.Tk):
    def __init__(self, logic_layer: architecture.LogicLayer) -> None:
        super().__init__()
        self.logic_layer = logic_layer

        self.tabs = Tabs(self, logic_layer)
        self.task_details = TaskDetails(self, logic_layer)

        self.tabs.grid(row=0, column=0)
        self.task_details.grid(row=0, column=1)

        self.title("graft")

    def run(self) -> None:
        # TODO: Set it up so any exceptions thrown by tkinter are logged
        self.mainloop()


def run(logic_layer: architecture.LogicLayer) -> None:
    gui = GUI(logic_layer)
    gui.run()
