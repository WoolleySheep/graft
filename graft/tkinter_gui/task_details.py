import functools
import tkinter as tk
from tkinter import scrolledtext, ttk
from typing import Self

from graft.architecture.logic import LogicLayer
from graft.domain import tasks
from graft.tkinter_gui import event_broker


class TaskDetails(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: LogicLayer) -> None:
        def update(event: event_broker.Event, self: Self) -> None:
            if not isinstance(event, event_broker.TaskSelected):
                raise TypeError

            self.task = event.task

            self.task_id.config(text=str(self.task))

            register = self.logic_layer.get_task_attributes_register_view()
            attributes = register[self.task]

            self.task_name.delete(0, tk.END)
            self.task_name.insert(0, str(attributes.name) or "")

            self.task_description.delete(1.0, tk.END)
            self.task_description.insert(1.0, str(attributes.description) or "")

            hierarchy_graph = self.logic_layer.get_hierarchy_graph_view()

            subtasks = []
            for subtask in hierarchy_graph.subtasks(self.task):
                attributes = register[subtask]
                subtasks.append(f"{subtask}: {attributes.name or ""}")

            self.subtasks_list.config(text="\n".join(subtasks))

            supertasks = []
            for supertask in hierarchy_graph.supertasks(self.task):
                attributes = register[supertask]
                supertasks.append(f"{supertask}: {attributes.name or ""}")

        def save(self: Self) -> None:
            assert self.task

            name = tasks.Name(self.task_name.get()) or None
            description = (
                tasks.Description(self.task_description.get(1.0, "end-1c")) or None
            )

            self.logic_layer.update_task_name(self.task, name)
            self.logic_layer.update_task_description(self.task, description)

            broker = event_broker.get_singleton()
            broker.publish(event_broker.SystemModified())

        super().__init__(master)
        self.logic_layer = logic_layer

        self.task: tasks.UID | None = None

        self.task_id = ttk.Label(self, text="")
        self.task_name = ttk.Entry(self)

        self.save_button = ttk.Button(
            self, text="Save", command=functools.partial(save, self=self)
        )

        self.task_description = scrolledtext.ScrolledText(self)

        self.subtasks_label = ttk.Label(self, text="Subtasks")
        self.subtasks_list = ttk.Label(self, text="")

        self.supertasks_label = ttk.Label(self, text="Supertasks")
        self.supertasks_list = ttk.Label(self, text="")

        self.task_id.grid(row=0, column=0)
        self.task_name.grid(row=0, column=1)
        self.save_button.grid(row=1, column=0, rowspan=2, columnspan=2)
        self.task_description.grid(row=3, column=0, rowspan=2)
        self.subtasks_label.grid(row=4, column=0)
        self.subtasks_list.grid(row=4, column=1)
        self.supertasks_label.grid(row=5, column=0)
        self.supertasks_list.grid(row=5, column=1)

        broker = event_broker.get_singleton()
        broker.subscribe(
            event_broker.TaskSelected, functools.partial(update, self=self)
        )
