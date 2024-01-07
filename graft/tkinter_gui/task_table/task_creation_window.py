import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.tkinter_gui import custom_events


class TaskIdLabel(tk.Frame):
    def __init__(self, master: tk.Misc, uid: tasks.UID) -> None:
        super().__init__(master=master)

        self.task_id_label = ttk.Label(self, text=f"Task ID: {uid}")
        self.task_id_label.grid()

class NameEntry(tk.Frame):

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master=master)

        self.name_label = ttk.Label(self, text="Name:")
        self.name_label.grid(column=0)

        self.name_input = ttk.Entry(self)
        self.name_input.grid(column=1)

    def get(self) -> tasks.Name | None:
        return tasks.Name(self.name_input.get()) or None

class DescriptionEntry(tk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master=master)

        self.description_label = ttk.Label(self, text="Description:")
        self.description_label.grid(column=0)

        self.description_input = ttk.Entry(self)
        self.description_input.grid(column=1)

    def get(self) -> tasks.Description | None:
        return tasks.Description(self.description_input.get()) or None


class TaskCreationWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        def create_task_using_entry_fields_then_destroy() -> None:
            logic_layer.create_task(name=self.name_entry.get(), description=self.description_entry.get())
            print("Generating event", custom_events.SYSTEM_UPDATE)
            self.event_generate(custom_events.SYSTEM_UPDATE)
            self.destroy()


        super().__init__(master=master)

        self.title("Create task")

        self.task_id_label = TaskIdLabel(self, uid=logic_layer.get_next_task_id())
        self.name_entry = NameEntry(self)
        self.description_entry = DescriptionEntry(self)

        self.confirm_button = ttk.Button(self, text="Confirm", command=create_task_using_entry_fields_then_destroy)

        self.task_id_label.grid(row=0)
        self.name_entry.grid(row=1)
        self.description_entry.grid(row=2)
        self.confirm_button.grid(row=3)



def create_task_creation_window(
    master: tk.Misc, logic_layer: architecture.LogicLayer
) -> None:
    TaskCreationWindow(master=master, logic_layer=logic_layer)
