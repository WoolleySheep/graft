import functools
import itertools
import logging
import tkinter as tk
from collections.abc import Callable
from tkinter import scrolledtext, ttk
from typing import Any, Final, Literal, ParamSpec, Self

from graft.architecture.logic import LogicLayer
from graft.domain import tasks
from graft.domain.tasks.progress import Progress
from graft.tkinter_gui import event_broker, helpers
from graft.tkinter_gui.helpers import importance_display, progress_display

_NEIGHBOURING_TASK_TABLES_ID_COLUMN_WIDTH_PIXELS = 30
_NEIGHBOURING_TASK_TABLES_NAME_COLUMN_WIDTH_PIXELS = 150
_NEIGHBOURING_TASK_TABLES_HEIGHT_ROWS = 5

P = ParamSpec("P")

logger: Final = logging.getLogger(__name__)


def _create_nieghbouring_task_table(master: tk.Misc) -> helpers.TaskTable:
    return helpers.TaskTable(
        master=master,
        id_column_width_pixels=_NEIGHBOURING_TASK_TABLES_ID_COLUMN_WIDTH_PIXELS,
        name_column_width_pixels=_NEIGHBOURING_TASK_TABLES_NAME_COLUMN_WIDTH_PIXELS,
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
        _ = fn(*args, **kwargs)
        return True

    return wrapper


class TaskDetails(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: LogicLayer) -> None:
        super().__init__(master)
        self._logic_layer = logic_layer

        self._task: tasks.UID | None = None

        self._task_id = ttk.Label(self)
        self._task_name = tk.StringVar(self)
        self._task_name_entry = ttk.Entry(
            self,
            textvariable=self._task_name,
            validate="focusout",
            validatecommand=make_return_true(
                self._on_name_entry_field_goes_out_of_focus
            ),
        )

        self._inferred_task_importance = ttk.Label(self)
        self._selected_importance = tk.StringVar(self)

        importance_menu_options = itertools.chain(
            (
                importance_display.format(importance)
                for importance in sorted(tasks.Importance, reverse=True)
            ),
            [""],
        )
        # Tkinter OptionMenu command should be passed a StringVar, but it is
        # instead passed a string. Hence the type ignore.
        self._task_importance_option_menu = ttk.OptionMenu(
            self,
            self._selected_importance,
            None,
            *importance_menu_options,
            command=self._on_importance_selected_from_option_button,  # type: ignore[reportArgumentType]
        )

        self._decrement_progress_button = ttk.Button(
            self, text="<", command=self._on_decrement_progress_button_clicked
        )
        self._task_progress_label = ttk.Label(self, text="")
        self._increment_progress_button = ttk.Button(
            self, text=">", command=self._on_increment_progress_button_clicked
        )

        self._save_description_button = ttk.Button(
            self,
            text="Save Description",
            command=self._on_save_description_button_clicked,
        )

        self._task_description_scrolled_text = scrolledtext.ScrolledText(self)

        self.subtasks_label = ttk.Label(self, text="Subtasks")
        self._subtasks_table = _create_nieghbouring_task_table(self)

        self.supertasks_label = ttk.Label(self, text="Supertasks")
        self._supertasks_table = _create_nieghbouring_task_table(self)

        self.dependee_tasks_label = ttk.Label(self, text="Dependee-tasks")
        self._dependee_tasks_table = _create_nieghbouring_task_table(self)

        self.dependent_tasks_label = ttk.Label(self, text="Dependent-tasks")
        self._dependent_tasks_table = _create_nieghbouring_task_table(self)

        self._task_id.grid(row=0, column=0)
        self._task_name_entry.grid(row=0, column=1, columnspan=3)
        self._inferred_task_importance.grid(row=1, column=0, columnspan=3)
        self._task_importance_option_menu.grid(row=1, column=0, columnspan=3)
        self._task_progress_label.grid(row=2, column=1)
        self._decrement_progress_button.grid(row=2, column=0)
        self._increment_progress_button.grid(row=2, column=2)
        self._task_description_scrolled_text.grid(row=3, column=0, columnspan=4)
        self._save_description_button.grid(row=4, column=0, columnspan=3)
        self.subtasks_label.grid(row=5, column=0, columnspan=2)
        self._subtasks_table.grid(row=6, column=0, columnspan=2)
        self.supertasks_label.grid(row=5, column=2, columnspan=2)
        self._supertasks_table.grid(row=6, column=2, columnspan=2)
        self.dependee_tasks_label.grid(row=7, column=0, columnspan=2)
        self._dependee_tasks_table.grid(row=8, column=0, columnspan=2)
        self.dependent_tasks_label.grid(row=7, column=2, columnspan=2)
        self._dependent_tasks_table.grid(row=8, column=2, columnspan=2)

        self._update_with_no_task()

        broker = event_broker.get_singleton()
        broker.subscribe(event_broker.TaskSelected, self._update)
        broker.subscribe(event_broker.SystemModified, self._update)

    def _update_with_task(self) -> None:
        assert self._task is not None

        self._task_id.config(text=str(self._task))

        register = self._logic_layer.get_task_system().attributes_register()
        attributes = register[self._task]

        self._task_name.set(str(attributes.name))
        self._task_name_entry.config(state=tk.NORMAL)

        system: tasks.SystemView = self._logic_layer.get_task_system()

        importance = system.get_importance(self._task)
        if system.has_inferred_importance(self._task):
            # If we can infer an importance, it will by definition not be None
            assert importance is not None
            self._task_importance_option_menu.grid_remove()
            formatted_importance = importance_display.format(importance)
            self._inferred_task_importance.config(text=formatted_importance)
            self._inferred_task_importance.grid()
        else:
            self._inferred_task_importance.grid_remove()
            formatted_importance = (
                importance_display.format(importance) if importance else ""
            )
            self._selected_importance.set(formatted_importance)
            self._task_importance_option_menu.grid()

        progress = system.get_progress(self._task)
        self._task_progress_label.config(text=progress_display.format(progress))

        if system.network_graph().hierarchy_graph().is_concrete(self._task):
            self._decrement_progress_button.grid()
            button_state = (
                tk.DISABLED if progress is tasks.Progress.NOT_STARTED else tk.NORMAL
            )
            self._decrement_progress_button.config(state=button_state)

            self._increment_progress_button.grid()
            button_state = (
                tk.DISABLED if progress is tasks.Progress.COMPLETED else tk.NORMAL
            )
            self._increment_progress_button.config(state=button_state)
        else:
            self._decrement_progress_button.grid_remove()
            self._increment_progress_button.grid_remove()

        self._task_description_scrolled_text.delete(1.0, tk.END)
        self._task_description_scrolled_text.insert(
            1.0,
            str(attributes.description),
        )
        self._task_description_scrolled_text.config(state=tk.NORMAL)

        hierarchy_graph = system.network_graph().hierarchy_graph()
        dependency_graph = system.network_graph().dependency_graph()

        subtasks_with_names = (
            (subtask, register[subtask].name)
            for subtask in hierarchy_graph.subtasks(self._task)
        )
        self._subtasks_table.update_tasks(subtasks_with_names)

        supertasks_with_names = (
            (supertask, register[supertask].name)
            for supertask in hierarchy_graph.supertasks(self._task)
        )
        self._supertasks_table.update_tasks(supertasks_with_names)

        dependee_tasks_with_names = (
            (dependee_task, register[dependee_task].name)
            for dependee_task in dependency_graph.dependee_tasks(self._task)
        )
        self._dependee_tasks_table.update_tasks(dependee_tasks_with_names)

        dependent_tasks_with_names = (
            (dependent_task, register[dependent_task].name)
            for dependent_task in dependency_graph.dependent_tasks(self._task)
        )
        self._dependent_tasks_table.update_tasks(dependent_tasks_with_names)

    def _update_with_no_task(self) -> None:
        assert self._task is None

        self._task_id.config(text="")
        self._task_name.set("")
        self._task_name_entry.config(state=tk.DISABLED)
        self._inferred_task_importance.grid()
        self._inferred_task_importance.config(text="")
        self._task_importance_option_menu.grid_remove()
        self._task_progress_label.config(text="")
        self._decrement_progress_button.grid_remove()
        self._increment_progress_button.grid_remove()
        self._task_description_scrolled_text.delete(1.0, tk.END)
        self._task_description_scrolled_text.config(state=tk.DISABLED)
        self._subtasks_table.update_tasks([])
        self._supertasks_table.update_tasks([])
        self._dependee_tasks_table.update_tasks([])
        self._dependent_tasks_table.update_tasks([])

    def _update(self, event: event_broker.Event) -> None:
        if isinstance(event, event_broker.TaskSelected):
            self._task = event.task
            self._update_with_task()
            return

        if isinstance(event, event_broker.SystemModified) and self._task:
            if self._task not in self._logic_layer.get_task_system():
                self._task = None
                self._update_with_no_task()
                return

            self._update_with_task()

    def _on_name_entry_field_goes_out_of_focus(self) -> None:
        logger.info("Name entry field lost focus")
        self._save_current_name()

    def _save_current_name(self) -> None:
        assert self._task is not None

        formatted_name = self._task_name.get()
        name = tasks.Name(formatted_name)

        try:
            self._logic_layer.update_task_name(task=self._task, name=name)
        except Exception as e:
            helpers.UnknownExceptionOperationFailedWindow(self, e)
            # Raise so it gets logged further up the chain
            raise

        broker = event_broker.get_singleton()
        broker.publish(event=event_broker.SystemModified())

    def _on_save_description_button_clicked(self) -> None:
        logger.info("Save description button clicked")
        self._save_current_description()

    def _save_current_description(self: Self) -> None:
        assert self._task

        formatted_description = self._task_description_scrolled_text.get(1.0, "end-1c")
        description = tasks.Description(formatted_description)

        try:
            self._logic_layer.update_task_description(self._task, description)
        except Exception as e:
            helpers.UnknownExceptionOperationFailedWindow(self, e)
            # Raise so it gets logged further up the chain
            raise

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())

    def _on_importance_selected_from_option_button(self, selection: str) -> None:
        logger.info("Importance [%s] selected from option menu", selection)
        self._save_current_importance()

    def _save_current_importance(self) -> None:
        assert self._task is not None

        formatted_importance = self._selected_importance.get()
        importance = (
            importance_display.parse(formatted_importance)
            if formatted_importance
            else None
        )

        try:
            self._logic_layer.update_task_importance(
                task=self._task, importance=importance
            )
        except Exception as e:
            helpers.UnknownExceptionOperationFailedWindow(self, e)
            # Raise so it gets logged further up the chain
            raise

        broker = event_broker.get_singleton()
        broker.publish(event=event_broker.SystemModified())

    def _on_increment_progress_button_clicked(self) -> None:
        logger.info("Increment progress button clicked")
        self._save_incremented_progress()

    def _save_incremented_progress(self) -> None:
        assert self._task

        current_progress = self._logic_layer.get_task_system().get_progress(self._task)
        incremented_progress = _get_progress_increment(current_progress)

        try:
            self._logic_layer.update_concrete_task_progress(
                self._task, incremented_progress
            )
        except Exception as e:
            helpers.UnknownExceptionOperationFailedWindow(self, exception=e)
            # Raise so it gets logged further up the chain
            raise

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())

    def _on_decrement_progress_button_clicked(self) -> None:
        logger.info("Decrement progress button clicked")
        self._save_decremented_progress()

    def _save_decremented_progress(self) -> None:
        assert self._task

        current_progress = self._logic_layer.get_task_system().get_progress(self._task)
        decremented_progress = _get_progress_decrement(current_progress)

        try:
            self._logic_layer.update_concrete_task_progress(
                self._task, decremented_progress
            )
        except Exception as e:
            helpers.UnknownExceptionOperationFailedWindow(self, exception=e)
            # Raise so it gets logged further up the chain
            raise

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())
