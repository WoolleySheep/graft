import tkinter as tk
from tkinter import scrolledtext, ttk

from graft import architecture
from graft.domain import tasks
from graft.tkinter_gui import event_broker


class TaskIdLabel(tk.Frame):
    def __init__(self, master: tk.Misc, uid: tasks.UID) -> None:
        super().__init__(master=master)

        self.task_id_label = ttk.Label(self, text=f"Task ID: {uid}")
        self.task_id_label.grid()


class NameEntry(tk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master=master)

        self.label = ttk.Label(self, text="Name:")
        self.label.grid(row=0, column=0)

        self.entry = ttk.Entry(self)
        self.entry.grid(row=0, column=1)

    def get(self) -> tasks.Name | None:
        return tasks.Name(self.entry.get()) or None


class DescriptionEntry(tk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master=master)

        self.label = ttk.Label(self, text="Description:")

        self.text_area = scrolledtext.ScrolledText(self)
        self.text_area.focus()

        self.label.grid(row=0, column=0)
        self.text_area.grid(row=0, column=1)

    def get(self) -> tasks.Description | None:
        return tasks.Description(self.text_area.get("1.0", "end-1c")) or None


class TaskCreationWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        def create_task_using_entry_fields_then_destroy_window() -> None:
            logic_layer.create_task(
                name=self.name_entry.get(), description=self.description_entry.get()
            )

            broker = event_broker.get_singleton()
            broker.publish(event_broker.SystemModified())
            self.destroy()

        super().__init__(master=master)

        self.title("Create task")

        self.task_id_label = TaskIdLabel(self, uid=logic_layer.get_next_task_id())
        self.name_entry = NameEntry(self)
        self.description_entry = DescriptionEntry(self)

        self.confirm_button = ttk.Button(
            self,
            text="Confirm",
            command=create_task_using_entry_fields_then_destroy_window,
        )

        self.task_id_label.grid(row=0, column=0)
        self.name_entry.grid(row=1, column=0)
        self.description_entry.grid(row=2, column=0)
        self.confirm_button.grid(row=3, column=0)


def create_task_creation_window(
    master: tk.Misc, logic_layer: architecture.LogicLayer
) -> None:
    TaskCreationWindow(master=master, logic_layer=logic_layer)
