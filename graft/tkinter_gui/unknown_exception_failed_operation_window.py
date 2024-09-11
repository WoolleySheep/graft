import tkinter as tk
import traceback
from tkinter import ttk

from graft.tkinter_gui.helpers import failed_operation_window


class UnknownExceptionOperationFailedWindow(
    failed_operation_window.OperationFailedWindow
):
    def __init__(self, master: tk.Misc, exception: Exception) -> None:
        super().__init__(master=master)
        self._restart_warning = ttk.Label(
            self, text="TO PRESERVE DATA INTEGRITY, RECOMMEND RESTARTING APP"
        )
        self._exception_type = ttk.Label(self, text=str(type(exception)))
        self._exception = ttk.Label(self, text=str(exception))
        self._traceback = ttk.Label(
            self,
            text="".join(
                traceback.format_exception(None, exception, exception.__traceback__)
            ),
        )

        self._restart_warning.grid(row=0, column=0)
        self._exception_type.grid(row=1, column=0)
        self._exception.grid(row=2, column=0)
        self._traceback.grid(row=3, column=0)
