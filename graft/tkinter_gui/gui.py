import tkinter as tk

from graft import architecture
from graft.tkinter_gui.tabs import Tabs


class GUI(tk.Tk):
    def __init__(self, logic_layer: architecture.LogicLayer) -> None:
        super().__init__()
        self.logic_layer = logic_layer
        self.title("graft")
        self.tabs = Tabs(self, logic_layer)
        self.tabs.pack()

    def run(self) -> None:
        self.mainloop()


def run(logic_layer: architecture.LogicLayer) -> None:
    gui = GUI(logic_layer)
    gui.run()

