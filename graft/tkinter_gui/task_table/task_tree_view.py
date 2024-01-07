import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.tkinter_gui import custom_events


class TaskTreeView(ttk.Treeview):


    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master, columns=("id", "name", "description"), show="headings")
        self._logic_layer = logic_layer

        self.heading("id", text="ID")
        self.heading("name", text="Name")
        self.heading("description", text="Description")

        self.update_tree()
        self.bind(custom_events.SYSTEM_UPDATE, lambda _: self.update_tree())

    def update_tree(self) -> None:
        print("Updating tree")
        self.delete(*self.get_children())

        for uid, attributes in self._logic_layer.get_task_attributes_register_view().items():
            formatted_uid = str(uid)
            formatted_name = str(attributes.name) if attributes.name is not None else ""
            formatted_description = (
                str(attributes.description)
                if attributes.description is not None
                else ""
            )
            self.insert(
                "",
                tk.END,
                values=[formatted_uid, formatted_name, formatted_description],
            )
