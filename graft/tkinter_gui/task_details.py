import functools
import tkinter as tk
from tkinter import scrolledtext, ttk
from typing import Self

from graft.architecture.logic import LogicLayer
from graft.domain import tasks
from graft.tkinter_gui import event_broker, helpers

_DECREMENT_PROGRESS_BUTTON_GRID_POSITION = (1, 0)
_INCREMENT_PROGRESS_BUTTON_GRID_POSITION = (1, 2)


class TaskDetails(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: LogicLayer) -> None:
        def update_with_task(self: Self) -> None:
            assert self.task is not None

            self.task_id.config(text=str(self.task))

            register = self.logic_layer.get_task_attributes_register_view()
            attributes = register[self.task]

            self.task_name.delete(0, tk.END)
            self.task_name.insert(
                0, str(attributes.name) if attributes.name is not None else ""
            )

            system = self.logic_layer.get_task_system_view()
            progress = system.get_progress(self.task)
            self.task_progress.config(text=progress.value)

            if logic_layer.get_task_hierarchy_graph_view().is_concrete(self.task):
                self.decrement_task_progress_button.grid()
                button_state = (
                    tk.DISABLED if progress is tasks.Progress.NOT_STARTED else tk.NORMAL
                )
                self.decrement_task_progress_button.config(state=button_state)

                self.increment_task_progress_button.grid()
                button_state = (
                    tk.DISABLED if progress is tasks.Progress.COMPLETED else tk.NORMAL
                )
                self.increment_task_progress_button.config(state=button_state)
            else:
                self.decrement_task_progress_button.grid_remove()
                self.increment_task_progress_button.grid_remove()

            self.task_description.delete(1.0, tk.END)
            self.task_description.insert(
                1.0,
                str(attributes.description)
                if attributes.description is not None
                else "",
            )

            hierarchy_graph = self.logic_layer.get_task_hierarchy_graph_view()

            subtasks = list[str]()
            for subtask in hierarchy_graph.subtasks(self.task):
                attributes = register[subtask]
                subtasks.append(f"{subtask}: {attributes.name or ""}")

            self.subtasks_list.config(text="\n".join(subtasks))

            supertasks = list[str]()
            for supertask in hierarchy_graph.supertasks(self.task):
                attributes = register[supertask]
                supertasks.append(f"{supertask}: {attributes.name or ""}")

            self.supertasks_list.config(text="\n".join(supertasks))

        def update_no_task(self: Self) -> None:
            assert self.task is None

            self.task_id.config(text="")
            self.task_name.delete(0, tk.END)
            self.task_progress.config(text="")
            self.decrement_task_progress_button.grid_remove()
            self.increment_task_progress_button.grid_remove()
            self.task_description.delete(1.0, tk.END)
            self.subtasks_list.config(text="")
            self.supertasks_list.config(text="")

        def update(event: event_broker.Event, self: Self) -> None:
            if isinstance(event, event_broker.TaskSelected):
                self.task = event.task
                update_with_task(self)
                return

            if isinstance(event, event_broker.SystemModified) and self.task:
                if self.task not in self.logic_layer.get_task_system_view():
                    self.task = None
                    update_no_task(self)
                    return

                update_with_task(self)

        def increment_progress(self: Self) -> None:
            assert self.task

            current_progress = self.logic_layer.get_task_system_view().get_progress(
                self.task
            )
            match current_progress:
                case tasks.Progress.NOT_STARTED:
                    incremented_progress = tasks.Progress.IN_PROGRESS
                case tasks.Progress.IN_PROGRESS:
                    incremented_progress = tasks.Progress.COMPLETED
                case tasks.Progress.COMPLETED:
                    raise ValueError("Cannot increment progress of completed task")

            try:
                self.logic_layer.update_task_progress(self.task, incremented_progress)
            except Exception as e:
                helpers.UnknownExceptionOperationFailedWindow(self, exception=e)
                return

            broker = event_broker.get_singleton()
            broker.publish(event_broker.SystemModified())

        def decrement_progress(self: Self) -> None:
            assert self.task

            current_progress = self.logic_layer.get_task_system_view().get_progress(
                self.task
            )
            match current_progress:
                case tasks.Progress.NOT_STARTED:
                    raise ValueError("Cannot decrement progress of not started task")
                case tasks.Progress.IN_PROGRESS:
                    decremented_progress = tasks.Progress.NOT_STARTED
                case tasks.Progress.COMPLETED:
                    decremented_progress = tasks.Progress.IN_PROGRESS

            try:
                self.logic_layer.update_task_progress(self.task, decremented_progress)
            except Exception as e:
                helpers.UnknownExceptionOperationFailedWindow(self, exception=e)
                return

            broker = event_broker.get_singleton()
            broker.publish(event_broker.SystemModified())

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

        self.decrement_task_progress_button = ttk.Button(
            self, text="<", command=functools.partial(decrement_progress, self=self)
        )
        self.task_progress = ttk.Label(self, text="")
        self.increment_task_progress_button = ttk.Button(
            self, text=">", command=functools.partial(increment_progress, self=self)
        )

        self.save_button = ttk.Button(
            self, text="Save", command=functools.partial(save, self=self)
        )

        self.task_description = scrolledtext.ScrolledText(self)

        self.subtasks_label = ttk.Label(self, text="Subtasks")
        self.subtasks_list = ttk.Label(self, text="")

        self.supertasks_label = ttk.Label(self, text="Supertasks")
        self.supertasks_list = ttk.Label(self, text="")

        self.task_id.grid(row=0, column=0)
        self.task_name.grid(row=0, column=1, columnspan=3)
        self.task_progress.grid(row=1, column=1)
        self.decrement_task_progress_button.grid(row=1, column=0)
        self.decrement_task_progress_button.grid_remove()
        self.increment_task_progress_button.grid(row=1, column=2)
        self.increment_task_progress_button.grid_remove()
        self.task_description.grid(row=2, column=0, columnspan=4)
        self.save_button.grid(row=3, column=0, columnspan=3)
        self.subtasks_label.grid(row=4, column=0)
        self.subtasks_list.grid(row=4, column=1)
        self.supertasks_label.grid(row=5, column=0)
        self.supertasks_list.grid(row=5, column=1)

        broker = event_broker.get_singleton()
        broker.subscribe(
            event_broker.TaskSelected, functools.partial(update, self=self)
        )
        broker.subscribe(
            event_broker.SystemModified, functools.partial(update, self=self)
        )
