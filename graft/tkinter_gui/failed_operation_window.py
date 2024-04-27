import tkinter as tk
from tkinter import ttk


class OperationFailedWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, exception: Exception) -> None:
        super().__init__(master=master)

        self.title("Operation failed")

        self.exception_type = ttk.Label(self, text=str(type(exception)))
        self.exception = ttk.Label(self, text=str(exception))

        self.exception_type.grid(row=0, column=0)
        self.exception.grid(row=1, column=0)


def create_operation_failed_window(master: tk.Misc, exception: Exception) -> None:
    OperationFailedWindow(master=master, exception=exception)
