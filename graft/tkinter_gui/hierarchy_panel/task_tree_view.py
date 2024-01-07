import functools
import tkinter as tk
from tkinter import ttk
from typing import Self

from graft import architecture
from graft.tkinter_gui import system_update_dispatcher


class TaskTreeView(ttk.Treeview):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        def update_tree(self: Self) -> None:
            self.delete(*self.get_children())

            for (
                uid,
                attributes,
            ) in self._logic_layer.get_task_attributes_register_view().items():
                formatted_uid = str(uid)
                formatted_name = (
                    str(attributes.name) if attributes.name is not None else ""
                )
                self.insert(
                    "",
                    tk.END,
                    values=[formatted_uid, formatted_name],
                )

        super().__init__(master, columns=("id", "name"), show="headings")
        self._logic_layer = logic_layer

        self.heading("id", text="ID")
        self.heading("name", text="Name")

        update_tree(self)

        dispatcher = system_update_dispatcher.get_singleton()
        dispatcher.add(functools.partial(update_tree, self=self))
