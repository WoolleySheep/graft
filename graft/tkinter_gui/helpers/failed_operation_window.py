import abc
import tkinter as tk


class OperationFailedWindow(tk.Toplevel, abc.ABC):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master=master)
        self.title("Operation failed")
