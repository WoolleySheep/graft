import logging
import tkinter as tk
from tkinter import scrolledtext, ttk

from graft import architecture
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import event_broker

logger = logging.getLogger(__name__)


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

    def get(self) -> tasks.Name:
        text = self.entry.get()
        return tasks.Name(text)


class DescriptionEntry(tk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master=master)

        self.label = ttk.Label(self, text="Description:")

        self.text_area = scrolledtext.ScrolledText(self)
        self.text_area.focus()

        self.label.grid(row=0, column=0)
        self.text_area.grid(row=0, column=1)

    def get(self) -> tasks.Description:
        text = self.text_area.get("1.0", "end-1c")
        return tasks.Description(text)


class TaskCreationWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self._logic_layer = logic_layer

        self.title("Create task")

        self._task_id_label = TaskIdLabel(self, uid=logic_layer.get_next_unused_task())
        self._name_entry = NameEntry(self)
        self._description_entry = DescriptionEntry(self)

        self._confirm_button = ttk.Button(
            self,
            text="Confirm",
            command=self._on_confirm_button_clicked,
        )

        self._task_id_label.grid(row=0, column=0)
        self._name_entry.grid(row=1, column=0)
        self._description_entry.grid(row=2, column=0)
        self._confirm_button.grid(row=3, column=0)

    def _on_confirm_button_clicked(self) -> None:
        logger.info("Confirm task creation button clicked")
        self._create_task_using_entry_fields_then_destroy_window()

    def _create_task_using_entry_fields_then_destroy_window(self) -> None:
        name = self._name_entry.get()
        description = self._description_entry.get()
        created_task = self._logic_layer.create_task(name=name, description=description)

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())
        broker.publish(event_broker.TaskSelected(created_task))
        self.destroy()
