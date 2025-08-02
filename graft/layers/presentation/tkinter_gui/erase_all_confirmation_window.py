import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.presentation.tkinter_gui import event_broker


class EraseAllConfirmationWindow(tk.Toplevel):
    def __init__(self, master: tk.Tk, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master)
        self._logic_layer = logic_layer

        self.title("Erase All Data")
        warning_label = ttk.Label(
            master=self,
            text="Are you sure you want to erase all data?\nThis cannot be undone.",
        )
        confirm_button = ttk.Button(
            master=self, text="Confirm", command=self._erase_all
        )

        warning_label.grid(row=0, column=0)
        confirm_button.grid(row=1, column=0)

    def _erase_all(self) -> None:
        self._logic_layer.erase()

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())
        self.destroy()
