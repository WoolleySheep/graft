import tkinter as tk
from tkinter import ttk

from graft.tkinter_gui.helpers import failed_operation_window


class UnknownExceptionOperationFailedWindow(
    failed_operation_window.OperationFailedWindow
):
    def __init__(self, master: tk.Misc, exception: Exception) -> None:
        super().__init__(master=master)

        self.exception_type = ttk.Label(self, text=str(type(exception)))
        self.exception = ttk.Label(self, text=str(exception))

        self.exception_type.grid(row=0, column=0)
        self.exception.grid(row=1, column=0)
