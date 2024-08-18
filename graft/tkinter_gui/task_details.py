import functools
import itertools
import tkinter as tk
from collections.abc import Callable
from tkinter import scrolledtext, ttk
from typing import Any, Literal, ParamSpec, Self

from graft.architecture.logic import LogicLayer
from graft.domain import tasks
from graft.domain.tasks.progress import Progress
from graft.tkinter_gui import event_broker, helpers

_NEIGHBOURING_TASK_TABLES_ID_COLUMN_WIDTH_CHARS = 5
_NEIGHBOURING_TASK_TABLES_NAME_COLUMN_WIDTH_CHARS = 10
_NEIGHBOURING_TASK_TABLES_HEIGHT_ROWS = 5

P = ParamSpec("P")


def _create_nieghbouring_task_table(master: tk.Misc) -> helpers.TaskTable:
    return helpers.TaskTable(
        master=master,
        id_column_width_chars=_NEIGHBOURING_TASK_TABLES_ID_COLUMN_WIDTH_CHARS,
        name_column_width_chars=_NEIGHBOURING_TASK_TABLES_NAME_COLUMN_WIDTH_CHARS,
        height_rows=_NEIGHBOURING_TASK_TABLES_HEIGHT_ROWS,
    )


def _get_progress_increment(progress: Progress) -> Progress:
    match progress:
        case tasks.Progress.NOT_STARTED:
            return tasks.Progress.IN_PROGRESS
        case tasks.Progress.IN_PROGRESS:
            return tasks.Progress.COMPLETED
        case tasks.Progress.COMPLETED:
            raise ValueError("Cannot increment progress of completed task")


def _get_progress_decrement(progress: Progress) -> Progress:
    match progress:
        case tasks.Progress.NOT_STARTED:
            raise ValueError("Cannot decrement progress of not started task")
        case tasks.Progress.IN_PROGRESS:
            return tasks.Progress.NOT_STARTED
        case tasks.Progress.COMPLETED:
            return tasks.Progress.IN_PROGRESS


def make_return_true(fn: Callable[P, Any]) -> Callable[P, Literal[True]]:
    """Wrap a function so that it always returns true."""

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Literal[True]:
        fn(*args, **kwargs)
        return True

    return wrapper


class TaskDetails(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: LogicLayer) -> None:
        def update_with_task(self: Self) -> None:
            assert self.task is not None

            self.task_id.config(text=str(self.task))

            register = self._logic_layer.get_task_system().attributes_register()
            attributes = register[self.task]

            self.task_name.set(str(attributes.name))
            self.task_name_entry.config(state=tk.NORMAL)

            system: tasks.SystemView = self._logic_layer.get_task_system()

            importance = system.get_importance(self.task)
            if system.has_inferred_importance(self.task):
                # If we can infer an importance, it will by definition not be None
                assert importance is not None
                self.task_importance_option_menu.grid_remove()
                formatted_importance = importance.value
                self.inferred_task_importance.config(text=formatted_importance)
                self.inferred_task_importance.grid()
            else:
                self.inferred_task_importance.grid_remove()
                formatted_importance = importance.value if importance else ""
                self.selected_importance.set(formatted_importance)
                self.task_importance_option_menu.grid()

            progress = system.get_progress(self.task)
            self.task_progress.config(text=progress.value)

            if system.hierarchy_graph().is_concrete(self.task):
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
                str(attributes.description),
            )
            self.task_description_scrolled_text.config(state=tk.NORMAL)

            hierarchy_graph = system.hierarchy_graph()
            dependency_graph = self._logic_layer.get_task_system().dependency_graph()

            subtasks_with_names = (
                (subtask, register[subtask].name)
                for subtask in hierarchy_graph.subtasks(self.task)
            )
            self._subtasks_table.update_tasks(subtasks_with_names)

            supertasks_with_names = (
                (supertask, register[supertask].name)
                for supertask in hierarchy_graph.supertasks(self.task)
            )
            self._supertasks_table.update_tasks(supertasks_with_names)

            dependee_tasks_with_names = (
                (dependee_task, register[dependee_task].name)
                for dependee_task in dependency_graph.dependee_tasks(self.task)
            )
            self._dependee_tasks_table.update_tasks(dependee_tasks_with_names)

            dependent_tasks_with_names = (
                (dependent_task, register[dependent_task].name)
                for dependent_task in dependency_graph.dependent_tasks(self.task)
            )
            self._dependent_tasks_table.update_tasks(dependent_tasks_with_names)

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
            self._subtasks_table.update_tasks([])
            self._supertasks_table.update_tasks([])
            self._dependee_tasks_table.update_tasks([])
            self._dependent_tasks_table.update_tasks([])

        def update(event: event_broker.Event, self: Self) -> None:
            if isinstance(event, event_broker.TaskSelected):
                self.task = event.task
                update_with_task(self)
                return

            if isinstance(event, event_broker.SystemModified) and self.task:
                if self.task not in self._logic_layer.get_task_system():
                    self.task = None
                    update_no_task(self)
                    return

                update_with_task(self)

        super().__init__(master)
        self._logic_layer = logic_layer

        self.task: tasks.UID | None = None

        self.task_id = ttk.Label(self)
        self.task_name = tk.StringVar(self)
        self.task_name_entry = ttk.Entry(
            self,
            textvariable=self.task_name,
            validate="focusout",
            validatecommand=make_return_true(self._save_current_name),
        )

        self.inferred_task_importance = ttk.Label(self)
        self.selected_importance = tk.StringVar(self)
        self.selected_importance.get()
        importance_menu_options = itertools.chain(
            (level.value for level in sorted(tasks.Importance, reverse=True)), [""]
        )

        self.task_importance_option_menu = ttk.OptionMenu(
            self,
            self.selected_importance,
            None,
            *importance_menu_options,
            command=lambda _: self._save_current_importance,
        )

        self.decrement_task_progress_button = ttk.Button(
            self, text="<", command=self._save_decremented_progress
        )
        self.task_progress = ttk.Label(self, text="")
        self.increment_task_progress_button = ttk.Button(
            self, text=">", command=self._save_incremented_progress
        )

        self.save_description_button = ttk.Button(
            self,
            text="Save Description",
            command=self._save_current_description,
        )

        self.task_description_scrolled_text = scrolledtext.ScrolledText(self)

        self.subtasks_label = ttk.Label(self, text="Subtasks")
        self._subtasks_table = _create_nieghbouring_task_table(self)

        self.supertasks_label = ttk.Label(self, text="Supertasks")
        self._supertasks_table = _create_nieghbouring_task_table(self)

        self.dependee_tasks_label = ttk.Label(self, text="Dependee-tasks")
        self._dependee_tasks_table = _create_nieghbouring_task_table(self)

        self.dependent_tasks_label = ttk.Label(self, text="Dependent-tasks")
        self._dependent_tasks_table = _create_nieghbouring_task_table(self)

        self.task_id.grid(row=0, column=0)
        self.task_name_entry.grid(row=0, column=1, columnspan=3)
        self.inferred_task_importance.grid(row=1, column=0, columnspan=3)
        self.task_importance_option_menu.grid(row=1, column=0, columnspan=3)
        self.task_progress.grid(row=2, column=1)
        self.decrement_task_progress_button.grid(row=2, column=0)
        self.increment_task_progress_button.grid(row=2, column=2)
        self.task_description_scrolled_text.grid(row=3, column=0, columnspan=4)
        self.save_description_button.grid(row=4, column=0, columnspan=3)
        self.subtasks_label.grid(row=5, column=0, columnspan=2)
        self._subtasks_table.grid(row=6, column=0, columnspan=2)
        self.supertasks_label.grid(row=5, column=2, columnspan=2)
        self._supertasks_table.grid(row=6, column=2, columnspan=2)
        self.dependee_tasks_label.grid(row=7, column=0, columnspan=2)
        self._dependee_tasks_table.grid(row=8, column=0, columnspan=2)
        self.dependent_tasks_label.grid(row=7, column=2, columnspan=2)
        self._dependee_tasks_table.grid(row=8, column=2, columnspan=2)

        update_no_task(self)

        broker = event_broker.get_singleton()
        broker.subscribe(
            event_broker.TaskSelected, functools.partial(update, self=self)
        )
        broker.subscribe(
            event_broker.SystemModified, functools.partial(update, self=self)
        )

    def _save_current_name(self) -> None:
        assert self.task is not None

        formatted_name = self.task_name.get()
        name = tasks.Name(formatted_name)

        try:
            self._logic_layer.update_task_name(task=self.task, name=name)
        except Exception as e:
            helpers.UnknownExceptionOperationFailedWindow(self, e)
            return

        broker = event_broker.get_singleton()
        broker.publish(event=event_broker.SystemModified())

    def _save_current_description(self: Self) -> None:
        assert self.task

        formatted_description = self.task_description_scrolled_text.get(1.0, "end-1c")
        description = tasks.Description(formatted_description)

        try:
            self._logic_layer.update_task_description(self.task, description)
        except Exception as e:
            helpers.UnknownExceptionOperationFailedWindow(self, e)
            return

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())

    def _save_current_importance(self) -> None:
        assert self.task is not None

        formatted_importance = self.selected_importance.get()
        importance = (
            tasks.Importance(formatted_importance) if formatted_importance else None
        )

        try:
            self._logic_layer.update_task_importance(
                task=self.task, importance=importance
            )
        except Exception as e:
            helpers.UnknownExceptionOperationFailedWindow(self, e)
            return

        broker = event_broker.get_singleton()
        broker.publish(event=event_broker.SystemModified())

    def _save_incremented_progress(self) -> None:
        assert self.task

        current_progress = self._logic_layer.get_task_system().get_progress(self.task)
        incremented_progress = _get_progress_increment(current_progress)

        try:
            self._logic_layer.update_task_progress(self.task, incremented_progress)
        except Exception as e:
            helpers.UnknownExceptionOperationFailedWindow(self, exception=e)
            return

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())

    def _save_decremented_progress(self) -> None:
        assert self.task

        current_progress = self._logic_layer.get_task_system().get_progress(self.task)
        decremented_progress = _get_progress_decrement(current_progress)

        try:
            self._logic_layer.update_task_progress(self.task, decremented_progress)
        except Exception as e:
            helpers.UnknownExceptionOperationFailedWindow(self, exception=e)
            return

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())
