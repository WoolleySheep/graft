import functools
import itertools
import tkinter as tk
from collections.abc import Callable
from tkinter import scrolledtext, ttk
from typing import Any, Literal, ParamSpec, Self

from graft.architecture.logic import LogicLayer
from graft.domain import tasks
from graft.tkinter_gui import event_broker, helpers

P = ParamSpec("P")


def make_return_true(fn: Callable[P, Any]) -> Callable[P, Literal[True]]:
    """Wrap a function so that it always returns true."""

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Literal[True]:
        fn(*args, **kwargs)
        return True

    return wrapper


class TaskDetails(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: LogicLayer) -> None:
        def update_name(self: Self) -> None:
            assert self.task is not None

            formatted_name = self.task_name.get()
            name = tasks.Name(formatted_name) if formatted_name else None

            try:
                logic_layer.update_task_name(task=self.task, name=name)
            except Exception as e:
                helpers.UnknownExceptionOperationFailedWindow(self, e)
                return

            broker = event_broker.get_singleton()
            broker.publish(event=event_broker.SystemModified())

        def update_importance(self: Self, formatted_importance: str) -> None:
            assert self.task is not None

            importance = (
                tasks.Importance(formatted_importance) if formatted_importance else None
            )

            try:
                logic_layer.update_task_importance(
                    task=self.task, importance=importance
                )
            except Exception as e:
                helpers.UnknownExceptionOperationFailedWindow(self, e)
                return

            broker = event_broker.get_singleton()
            broker.publish(event=event_broker.SystemModified())

        def update_with_task(self: Self) -> None:
            assert self.task is not None

            self.task_id.config(text=str(self.task))

            register = self.logic_layer.get_task_attributes_register_view()
            attributes = register[self.task]

            self.task_name.set(
                str(attributes.name) if attributes.name is not None else ""
            )
            self.task_name_entry.config(state=tk.NORMAL)

            system: tasks.SystemView = self.logic_layer.get_task_system_view()

            importance = system.get_importance(self.task)
            if importance is None or not isinstance(importance, set):
                self.inferred_task_importance.grid_remove()
                self.selected_importance.set(importance.value if importance else "")
                self.task_importance_option_menu.grid()
            else:
                self.task_importance_option_menu.grid_remove()
                formatted_importance = " | ".join(
                    level.value for level in sorted(importance)
                )
                self.inferred_task_importance.config(text=formatted_importance)
                self.inferred_task_importance.grid()

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

            self.task_description_scrolled_text.delete(1.0, tk.END)
            self.task_description_scrolled_text.insert(
                1.0,
                str(attributes.description)
                if attributes.description is not None
                else "",
            )
            self.task_description_scrolled_text.config(state=tk.NORMAL)

            hierarchy_graph = self.logic_layer.get_task_hierarchy_graph_view()

            formatted_subtasks = (
                f"{subtask}: {register[subtask].name or ""}"
                for subtask in hierarchy_graph.subtasks(self.task)
            )
            self.subtasks_list.config(text="\n".join(formatted_subtasks))

            formatted_supertasks = (
                f"{supertask}: {register[supertask].name or ""}"
                for supertask in hierarchy_graph.supertasks(self.task)
            )
            self.supertasks_list.config(text="\n".join(formatted_supertasks))

            dependency_graph = self.logic_layer.get_task_dependency_graph_view()

            formatted_dependee_tasks = (
                f"{supertask}: {register[supertask].name or ""}"
                for supertask in dependency_graph.dependee_tasks(self.task)
            )
            self.dependee_tasks_list.config(text="\n".join(formatted_dependee_tasks))

            formatted_dependent_tasks = (
                f"{supertask}: {register[supertask].name or ""}"
                for supertask in dependency_graph.dependent_tasks(self.task)
            )
            self.dependent_tasks_list.config(text="\n".join(formatted_dependent_tasks))

        def update_no_task(self: Self) -> None:
            assert self.task is None

            self.task_id.config(text="")
            self.task_name.set("")
            self.task_name_entry.config(state=tk.DISABLED)
            self.inferred_task_importance.grid()
            self.inferred_task_importance.config(text="")
            self.task_importance_option_menu.grid_remove()
            self.task_progress.config(text="")
            self.decrement_task_progress_button.grid_remove()
            self.increment_task_progress_button.grid_remove()
            self.task_description_scrolled_text.delete(1.0, tk.END)
            self.task_description_scrolled_text.config(state=tk.DISABLED)
            self.subtasks_list.config(text="")
            self.supertasks_list.config(text="")
            self.dependee_tasks_list.config(text="")
            self.dependent_tasks_list.config(text="")

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

        def update_description(self: Self) -> None:
            assert self.task

            description = (
                tasks.Description(
                    self.task_description_scrolled_text.get(1.0, "end-1c")
                )
                or None
            )

            try:
                self.logic_layer.update_task_description(self.task, description)
            except Exception as e:
                helpers.UnknownExceptionOperationFailedWindow(self, e)
                return

            broker = event_broker.get_singleton()
            broker.publish(event_broker.SystemModified())

        super().__init__(master)
        self.logic_layer = logic_layer

        self.task: tasks.UID | None = None

        self.task_id = ttk.Label(self)
        self.task_name = tk.StringVar(self)
        self.task_name_entry = ttk.Entry(
            self,
            textvariable=self.task_name,
            validate="focusout",
            validatecommand=make_return_true(functools.partial(update_name, self)),
        )

        self.inferred_task_importance = ttk.Label(self)
        self.selected_importance = tk.StringVar(self)
        importance_menu_options = itertools.chain(
            [""], (level.value for level in tasks.Importance)
        )
        self.task_importance_option_menu = ttk.OptionMenu(
            self,
            self.selected_importance,
            None,
            *importance_menu_options,
            command=functools.partial(update_importance, self),
        )

        self.decrement_task_progress_button = ttk.Button(
            self, text="<", command=functools.partial(decrement_progress, self=self)
        )
        self.task_progress = ttk.Label(self, text="")
        self.increment_task_progress_button = ttk.Button(
            self, text=">", command=functools.partial(increment_progress, self=self)
        )

        self.save_description_button = ttk.Button(
            self,
            text="Save Description",
            command=functools.partial(update_description, self=self),
        )

        self.task_description_scrolled_text = scrolledtext.ScrolledText(self)

        self.subtasks_label = ttk.Label(self, text="Subtasks")
        self.subtasks_list = ttk.Label(self)

        self.supertasks_label = ttk.Label(self, text="Supertasks")
        self.supertasks_list = ttk.Label(self)

        self.dependee_tasks_label = ttk.Label(self, text="Dependee-tasks")
        self.dependee_tasks_list = ttk.Label(self)

        self.dependent_tasks_label = ttk.Label(self, text="Dependent-tasks")
        self.dependent_tasks_list = ttk.Label(self)

        self.task_id.grid(row=0, column=0)
        self.task_name_entry.grid(row=0, column=1, columnspan=3)
        self.inferred_task_importance.grid(row=1, column=0, columnspan=3)
        self.task_importance_option_menu.grid(row=1, column=0, columnspan=3)
        self.task_progress.grid(row=2, column=1)
        self.decrement_task_progress_button.grid(row=2, column=0)
        self.increment_task_progress_button.grid(row=2, column=2)
        self.task_description_scrolled_text.grid(row=3, column=0, columnspan=4)
        self.save_description_button.grid(row=4, column=0, columnspan=3)
        self.subtasks_label.grid(row=5, column=0)
        self.subtasks_list.grid(row=5, column=1, columnspan=3)
        self.supertasks_label.grid(row=6, column=0)
        self.supertasks_list.grid(row=6, column=1, columnspan=3)
        self.dependee_tasks_label.grid(row=7, column=0)
        self.dependee_tasks_list.grid(row=7, column=1, columnspan=3)
        self.dependent_tasks_label.grid(row=8, column=0)
        self.dependent_tasks_list.grid(row=8, column=1, columnspan=3)

        update_no_task(self)

        broker = event_broker.get_singleton()
        broker.subscribe(
            event_broker.TaskSelected, functools.partial(update, self=self)
        )
        broker.subscribe(
            event_broker.SystemModified, functools.partial(update, self=self)
        )
