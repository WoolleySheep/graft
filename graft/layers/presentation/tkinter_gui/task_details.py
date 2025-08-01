import functools
import itertools
import logging
import tkinter as tk
from collections.abc import Callable
from tkinter import scrolledtext, ttk
from typing import Any, Final, Literal, Self

from graft.architecture.logic import LogicLayer
from graft.domain import tasks
from graft.domain.tasks.progress import Progress
from graft.layers.presentation.tkinter_gui import event_broker, helpers
from graft.layers.presentation.tkinter_gui.domain_visual_language import (
    get_task_colour_by_importance,
    get_task_colour_by_progress,
)
from graft.layers.presentation.tkinter_gui.helpers import (
    importance_display,
    progress_display,
)
from graft.layers.presentation.tkinter_gui.helpers.update_task_progress_error_windows import (
    convert_update_task_progress_exceptions_to_error_windows,
)
from graft.layers.presentation.tkinter_gui.tabs.delete_task_confirmation_window import (
    TaskDeletionConfirmationWindow,
)
from graft.layers.presentation.tkinter_gui.tabs.dependency_panel.creation_deletion_panel.dependency_creation_window import (
    DependencyCreationWindow,
)
from graft.layers.presentation.tkinter_gui.tabs.dependency_panel.creation_deletion_panel.dependency_deletion_window import (
    DependencyDeletionWindow,
)
from graft.layers.presentation.tkinter_gui.tabs.hierarchy_panel.creation_deletion_panel.hierarchy_creation_window import (
    HierarchyCreationWindow,
)
from graft.layers.presentation.tkinter_gui.tabs.hierarchy_panel.creation_deletion_panel.hierarchy_deletion_window import (
    HierarchyDeletionWindow,
)
from graft.layers.presentation.tkinter_gui.tabs.task_panel.creation_deletion_panel.task_creation_window import (
    TaskCreationWindow,
)

_NEIGHBOURING_TASK_TABLES_ID_COLUMN_WIDTH_PIXELS = 30
_NEIGHBOURING_TASK_TABLES_NAME_COLUMN_WIDTH_PIXELS = 150
_NEIGHBOURING_TASK_TABLES_NUMBER_OF_DISPLAYED_ROWS = 5

_NO_IMPORTANCE_IMPORTANCE_MENU_OPTION_TEXT: Final = " "

logger: Final = logging.getLogger(__name__)


def _create_nieghbouring_task_table(master: tk.Misc) -> helpers.TaskTableWithName:
    return helpers.TaskTableWithName(
        master=master,
        id_column_width_pixels=_NEIGHBOURING_TASK_TABLES_ID_COLUMN_WIDTH_PIXELS,
        name_column_width_pixels=_NEIGHBOURING_TASK_TABLES_NAME_COLUMN_WIDTH_PIXELS,
        number_of_rows_displayed=_NEIGHBOURING_TASK_TABLES_NUMBER_OF_DISPLAYED_ROWS,
    )


def _get_progress_increment(progress: Progress) -> Progress:
    match progress:
        case tasks.Progress.NOT_STARTED:
            return tasks.Progress.IN_PROGRESS
        case tasks.Progress.IN_PROGRESS:
            return tasks.Progress.COMPLETED
        case tasks.Progress.COMPLETED:
            msg = "Cannot increment progress of completed task"
            raise ValueError(msg)


def _get_progress_decrement(progress: Progress) -> Progress:
    match progress:
        case tasks.Progress.NOT_STARTED:
            msg = "Cannot decrement progress of not started task"
            raise ValueError(msg)
        case tasks.Progress.IN_PROGRESS:
            return tasks.Progress.NOT_STARTED
        case tasks.Progress.COMPLETED:
            return tasks.Progress.IN_PROGRESS


def make_return_true[**P](fn: Callable[P, Any]) -> Callable[P, Literal[True]]:
    """Wrap a function so that it always returns true."""

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Literal[True]:
        _ = fn(*args, **kwargs)
        return True

    return wrapper


def _parse_importance_menu_option(text: str) -> tasks.Importance | None:
    return (
        importance_display.parse(text)
        if text != _NO_IMPORTANCE_IMPORTANCE_MENU_OPTION_TEXT
        else None
    )


def _format_as_importance_menu_option(importance: tasks.Importance | None) -> str:
    return (
        importance_display.format(importance)
        if importance is not None
        else _NO_IMPORTANCE_IMPORTANCE_MENU_OPTION_TEXT
    )


class TaskDetails(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: LogicLayer) -> None:
        super().__init__(master)
        self._logic_layer = logic_layer

        self._task: tasks.UID | None = None

        self._header_section = ttk.Frame(master=self)
        self._create_task_button = ttk.Button(
            master=self._header_section, text="+", command=self._create_new_task
        )
        self._delete_task_button = ttk.Button(
            master=self._header_section, text="x", command=self._delete_task
        )

        self._identifier_section = ttk.Frame(master=self._header_section)
        self._task_id = ttk.Label(master=self._identifier_section)
        self._task_name = tk.StringVar(master=self._identifier_section)
        self._task_name_entry = ttk.Entry(
            master=self._identifier_section,
            textvariable=self._task_name,
            validate="focusout",
            validatecommand=make_return_true(
                self._on_name_entry_field_goes_out_of_focus
            ),
        )

        self._imporance_section = ttk.Frame(master=self._header_section)
        self._importance_label = ttk.Label(self._imporance_section, text="Importance:")
        self._inferred_task_importance = ttk.Label(master=self._imporance_section)
        self._selected_importance = tk.StringVar(master=self._imporance_section)
        self._selected_importance_backup: tasks.Importance | None = None

        self._importance_menu_options_to_colour_map = dict(
            itertools.chain(
                (
                    (
                        importance_display.format(importance),
                        str(get_task_colour_by_importance(importance)),
                    )
                    for importance in sorted(tasks.Importance, reverse=True)
                ),
                [(_NO_IMPORTANCE_IMPORTANCE_MENU_OPTION_TEXT, "grey")],
            ),
        )
        # Tkinter OptionMenu command should be passed a StringVar, but it is
        # instead passed a string. Hence the type ignore.
        self._task_importance_option_menu = ttk.OptionMenu(
            self._imporance_section,
            self._selected_importance,
            None,
            *self._importance_menu_options_to_colour_map.keys(),
            command=self._on_importance_selected_from_option_button,  # type: ignore[reportArgumentType]
        )
        menu = self._task_importance_option_menu.nametowidget(
            self._task_importance_option_menu.cget("menu")
        )
        for menu_option, colour in self._importance_menu_options_to_colour_map.items():
            index = menu.index(menu_option)
            menu.entryconfigure(index, background=colour)

        self._progress_section = ttk.Frame(master=self._header_section)
        self._progress_label = ttk.Label(master=self._progress_section, text="Progress")
        self._decrement_progress_button = ttk.Button(
            master=self._progress_section,
            text="<",
            command=self._on_decrement_progress_button_clicked,
        )
        self._task_progress_label = ttk.Label(master=self._progress_section, text="")
        self._increment_progress_button = ttk.Button(
            master=self._progress_section,
            text=">",
            command=self._on_increment_progress_button_clicked,
        )

        self._description_section = ttk.Frame(master=self)
        self._task_description_scrolled_text = scrolledtext.ScrolledText(
            master=self._description_section
        )
        self._task_description_scrolled_text.bind(
            "<FocusOut>",
            lambda _: self._on_description_scrolled_text_goes_out_of_focus(),
        )

        self._neighbours_section = ttk.Frame(master=self)

        self._subtasks_section = ttk.Frame(master=self._neighbours_section)
        self._subtasks_label = ttk.Label(master=self._subtasks_section, text="Subtasks")
        self._subtask_add_button = ttk.Button(
            master=self._subtasks_section,
            text="+",
            command=self._open_subtask_hierarchy_creation_window,
        )
        self._subtask_remove_button = ttk.Button(
            master=self._subtasks_section,
            text="-",
            command=self._open_subtask_hierarchy_deletion_window,
        )
        self._subtasks_table = _create_nieghbouring_task_table(
            master=self._subtasks_section
        )

        self._supertasks_section = ttk.Frame(master=self._neighbours_section)
        self._supertasks_label = ttk.Label(
            master=self._supertasks_section, text="Supertasks"
        )
        self._supertask_add_button = ttk.Button(
            master=self._supertasks_section,
            text="+",
            command=self._open_supertask_hierarchy_creation_window,
        )
        self._supertask_remove_button = ttk.Button(
            master=self._supertasks_section,
            text="-",
            command=self._open_supertask_hierarchy_deletion_window,
        )
        self._supertasks_table = _create_nieghbouring_task_table(
            master=self._supertasks_section
        )

        self._dependee_tasks_section = ttk.Frame(master=self._neighbours_section)
        self._dependee_tasks_label = ttk.Label(
            master=self._dependee_tasks_section, text="Dependee-tasks"
        )
        self._dependee_task_add_button = ttk.Button(
            master=self._dependee_tasks_section,
            text="+",
            command=self._open_dependee_task_dependency_creation_window,
        )
        self._dependee_task_remove_button = ttk.Button(
            master=self._dependee_tasks_section,
            text="-",
            command=self._open_dependee_task_dependency_deletion_window,
        )
        self._dependee_tasks_table = _create_nieghbouring_task_table(
            master=self._dependee_tasks_section
        )

        self._dependent_tasks_section = ttk.Frame(master=self._neighbours_section)
        self._dependent_tasks_label = ttk.Label(
            master=self._dependent_tasks_section, text="Dependent-tasks"
        )
        self._dependent_task_add_button = ttk.Button(
            master=self._dependent_tasks_section,
            text="+",
            command=self._open_dependent_task_dependency_creation_window,
        )
        self._dependent_task_remove_button = ttk.Button(
            master=self._dependent_tasks_section,
            text="-",
            command=self._open_dependent_task_dependency_deletion_window,
        )
        self._dependent_tasks_table = _create_nieghbouring_task_table(
            master=self._dependent_tasks_section
        )

        self._header_section.grid(row=0)
        self._description_section.grid(row=1)
        self._neighbours_section.grid(row=2)

        self._create_task_button.grid(row=0, column=0, rowspan=3)
        self._delete_task_button.grid(row=0, column=2, rowspan=3)
        self._identifier_section.grid(row=0, column=1)
        self._imporance_section.grid(row=1, column=1)
        self._progress_section.grid(row=2, column=1)

        self._task_id.grid(row=0, column=0)
        self._task_name_entry.grid(row=0, column=1)

        self._importance_label.grid(row=0, column=0)
        self._inferred_task_importance.grid(row=0, column=1)
        self._task_importance_option_menu.grid(row=0, column=1)

        self._progress_label.grid(row=0, column=0)
        self._decrement_progress_button.grid(row=0, column=1)
        self._task_progress_label.grid(row=0, column=2)
        self._increment_progress_button.grid(row=0, column=3)

        self._task_description_scrolled_text.grid(row=0, column=0)

        self._supertasks_section.grid(row=0, column=1)
        self._subtasks_section.grid(row=2, column=1)
        self._dependee_tasks_section.grid(row=1, column=0)
        self._dependent_tasks_section.grid(row=1, column=2)

        self._supertasks_label.grid(row=0, column=0)
        self._supertask_add_button.grid(row=0, column=1)
        self._supertask_remove_button.grid(row=0, column=2)
        self._supertasks_table.grid(row=1, column=0, columnspan=3)

        self._subtasks_label.grid(row=0, column=0)
        self._subtask_add_button.grid(row=0, column=1)
        self._subtask_remove_button.grid(row=0, column=2)
        self._subtasks_table.grid(row=1, column=0, columnspan=3)

        self._dependee_tasks_label.grid(row=0, column=0)
        self._dependee_task_add_button.grid(row=0, column=1)
        self._dependee_task_remove_button.grid(row=0, column=2)
        self._dependee_tasks_table.grid(row=1, column=0, columnspan=3)

        self._dependent_tasks_label.grid(row=0, column=0)
        self._dependent_task_add_button.grid(row=0, column=1)
        self._dependent_task_remove_button.grid(row=0, column=2)
        self._dependent_tasks_table.grid(row=1, column=0, columnspan=3)

        self._update_with_no_task()

        self.winfo_toplevel().protocol("WM_DELETE_WINDOW", self._on_closing)

        broker = event_broker.get_singleton()
        broker.subscribe(event_broker.TaskSelected, self._update)
        broker.subscribe(event_broker.SystemModified, self._update)

    def _update_with_task(self) -> None:
        assert self._task is not None

        self._task_id.config(text=f"ID-{self._task}")

        register = self._logic_layer.get_task_system().attributes_register()
        attributes = register[self._task]

        self._delete_task_button.config(state=tk.NORMAL)

        self._task_name.set(str(attributes.name))
        self._task_name_entry.config(state=tk.NORMAL)

        system: tasks.SystemView = self._logic_layer.get_task_system()

        importance = system.get_importance(self._task)
        if system.has_inferred_importance(self._task):
            # If we can infer an importance, it will by definition not be None
            assert importance is not None
            self._task_importance_option_menu.grid_remove()
            formatted_importance = importance_display.format(importance)
            self._inferred_task_importance.config(
                text=formatted_importance,
                background=str(get_task_colour_by_importance(importance)),
            )
            self._inferred_task_importance.grid()
        else:
            self._inferred_task_importance.grid_remove()
            formatted_importance = (
                importance_display.format(importance) if importance else " "
            )
            bg = (
                str(get_task_colour_by_importance(importance))
                if importance is not None
                else "grey"
            )
            style = ttk.Style()
            style.configure("Custom.TMenubutton", background=bg)
            self._task_importance_option_menu.configure(style="Custom.TMenubutton")
            self._selected_importance.set(formatted_importance)
            self._selected_importance_backup = importance
            self._task_importance_option_menu.grid()

        progress = system.get_progress(self._task)
        progress_text = progress_display.format(progress)
        if progress is Progress.NOT_STARTED:
            if system.is_active_task(self._task):
                active_label = "active"
                progress_colour = "blue"
            else:
                active_label = "inactive"
                progress_colour = "grey"
            progress_text = f"{progress_text} [{active_label}]"
        else:
            progress_colour = str(get_task_colour_by_progress(progress))

        self._task_progress_label.config(
            text=progress_text,
            background=progress_colour,
        )

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
        self._subtask_add_button.config(state=tk.NORMAL)
        self._subtask_remove_button.config(state=tk.NORMAL)

        supertasks_with_names = (
            (supertask, register[supertask].name)
            for supertask in hierarchy_graph.supertasks(self._task)
        )
        self._supertasks_table.update_tasks(supertasks_with_names)
        self._supertask_add_button.config(state=tk.NORMAL)
        self._supertask_remove_button.config(state=tk.NORMAL)

        dependee_tasks_with_names = (
            (dependee_task, register[dependee_task].name)
            for dependee_task in dependency_graph.dependee_tasks(self._task)
        )
        self._dependee_tasks_table.update_tasks(dependee_tasks_with_names)
        self._dependee_task_add_button.config(state=tk.NORMAL)
        self._dependee_task_remove_button.config(state=tk.NORMAL)

        dependent_tasks_with_names = (
            (dependent_task, register[dependent_task].name)
            for dependent_task in dependency_graph.dependent_tasks(self._task)
        )
        self._dependent_tasks_table.update_tasks(dependent_tasks_with_names)
        self._dependent_task_add_button.config(state=tk.NORMAL)
        self._dependent_task_remove_button.config(state=tk.NORMAL)

    def _update_with_no_task(self) -> None:
        assert self._task is None

        self._delete_task_button.config(state=tk.DISABLED)
        self._task_id.config(text="ID-XXXX")
        self._task_name.set("")
        self._task_name_entry.config(state=tk.DISABLED)
        self._inferred_task_importance.grid()
        self._inferred_task_importance.config(text="", background="")
        self._task_importance_option_menu.grid_remove()
        self._task_progress_label.config(text="", background="")
        self._decrement_progress_button.grid_remove()
        self._increment_progress_button.grid_remove()
        self._task_description_scrolled_text.delete(1.0, tk.END)
        self._task_description_scrolled_text.config(state=tk.DISABLED)
        self._subtasks_table.update_tasks([])
        self._subtask_add_button.config(state=tk.DISABLED)
        self._subtask_remove_button.config(state=tk.DISABLED)
        self._supertasks_table.update_tasks([])
        self._supertask_add_button.config(state=tk.DISABLED)
        self._supertask_remove_button.config(state=tk.DISABLED)
        self._dependee_tasks_table.update_tasks([])
        self._dependee_task_add_button.config(state=tk.DISABLED)
        self._dependee_task_remove_button.config(state=tk.DISABLED)
        self._dependent_tasks_table.update_tasks([])
        self._dependent_task_add_button.config(state=tk.DISABLED)
        self._dependent_task_remove_button.config(state=tk.DISABLED)

    def _update(self, event: event_broker.Event) -> None:
        if isinstance(event, event_broker.TaskSelected):
            self._task = event.task
            self._update_with_task()
            return

        if isinstance(event, event_broker.SystemModified) and self._task:
            if self._task not in self._logic_layer.get_task_system().tasks():
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

        self._logic_layer.update_task_name(task=self._task, name=name)

        broker = event_broker.get_singleton()
        broker.publish(event=event_broker.SystemModified())

    def _save_current_description(self: Self) -> None:
        assert self._task

        formatted_description = self._task_description_scrolled_text.get(1.0, "end-1c")
        description = tasks.Description(formatted_description)

        self._logic_layer.update_task_description(self._task, description)

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())

    def _on_importance_selected_from_option_button(self, selection: str) -> None:
        logger.info("Importance [%s] selected from option menu", selection)
        self._save_current_importance()

    def _save_current_importance(self) -> None:
        assert self._task is not None

        importance = _parse_importance_menu_option(self._selected_importance.get())

        if not convert_update_task_progress_exceptions_to_error_windows(
            functools.partial(
                self._logic_layer.update_task_importance,
                task=self._task,
                importance=importance,
            ),
            get_task_name=lambda task: self._logic_layer.get_task_system()
            .attributes_register()[task]
            .name,
            master=self,
        ):
            # Reset the importance to what it was before the user tried to change it
            self._selected_importance.set(
                _format_as_importance_menu_option(self._selected_importance_backup)
            )
            return

        # Operation succeeded, so update the backup
        self._selected_importance_backup = importance

        broker = event_broker.get_singleton()
        broker.publish(event=event_broker.SystemModified())

    def _on_increment_progress_button_clicked(self) -> None:
        logger.info("Increment progress button clicked")
        self._save_incremented_progress()

    def _save_incremented_progress(self) -> None:
        assert self._task

        current_progress = self._logic_layer.get_task_system().get_progress(self._task)
        incremented_progress = _get_progress_increment(current_progress)

        if not convert_update_task_progress_exceptions_to_error_windows(
            functools.partial(
                self._logic_layer.update_concrete_task_progress,
                self._task,
                incremented_progress,
            ),
            get_task_name=lambda task: self._logic_layer.get_task_system()
            .attributes_register()[task]
            .name,
            master=self,
        ):
            return

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())

    def _on_decrement_progress_button_clicked(self) -> None:
        logger.info("Decrement progress button clicked")
        self._save_decremented_progress()

    def _save_decremented_progress(self) -> None:
        assert self._task

        current_progress = self._logic_layer.get_task_system().get_progress(self._task)
        decremented_progress = _get_progress_decrement(current_progress)

        if not convert_update_task_progress_exceptions_to_error_windows(
            functools.partial(
                self._logic_layer.update_concrete_task_progress,
                self._task,
                decremented_progress,
            ),
            get_task_name=lambda task: self._logic_layer.get_task_system()
            .attributes_register()[task]
            .name,
            master=self,
        ):
            return

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())

    def _open_supertask_hierarchy_creation_window(self) -> None:
        assert self._task is not None

        HierarchyCreationWindow(
            master=self,
            get_tasks=lambda: self._logic_layer.get_task_system().tasks(),
            get_incomplete_tasks=lambda: tasks.get_incomplete_system(
                self._logic_layer.get_task_system()
            ).tasks(),
            get_task_name=lambda task: self._logic_layer.get_task_system()
            .attributes_register()[task]
            .name,
            create_hierarchy=self._logic_layer.create_task_hierarchy,
            fixed_subtask=self._task,
        )

    def _open_subtask_hierarchy_creation_window(self) -> None:
        assert self._task is not None

        HierarchyCreationWindow(
            master=self,
            get_tasks=lambda: self._logic_layer.get_task_system().tasks(),
            get_incomplete_tasks=lambda: tasks.get_incomplete_system(
                self._logic_layer.get_task_system()
            ).tasks(),
            get_task_name=lambda task: self._logic_layer.get_task_system()
            .attributes_register()[task]
            .name,
            create_hierarchy=self._logic_layer.create_task_hierarchy,
            fixed_supertask=self._task,
        )

    def _open_dependee_task_dependency_creation_window(self) -> None:
        assert self._task is not None

        DependencyCreationWindow(
            master=self,
            get_tasks=lambda: self._logic_layer.get_task_system().tasks(),
            get_incomplete_tasks=lambda: tasks.get_incomplete_system(
                self._logic_layer.get_task_system()
            ).tasks(),
            get_task_name=lambda task: self._logic_layer.get_task_system()
            .attributes_register()[task]
            .name,
            create_dependency=self._logic_layer.create_task_dependency,
            fixed_dependent_task=self._task,
        )

    def _open_dependent_task_dependency_creation_window(self) -> None:
        assert self._task is not None

        DependencyCreationWindow(
            master=self,
            get_tasks=lambda: self._logic_layer.get_task_system().tasks(),
            get_incomplete_tasks=lambda: tasks.get_incomplete_system(
                self._logic_layer.get_task_system()
            ).tasks(),
            get_task_name=lambda task: self._logic_layer.get_task_system()
            .attributes_register()[task]
            .name,
            create_dependency=self._logic_layer.create_task_dependency,
            fixed_dependee_task=self._task,
        )

    def _open_supertask_hierarchy_deletion_window(self) -> None:
        assert self._task is not None

        HierarchyDeletionWindow(
            master=self,
            hierarchy_options=(
                (supertask, self._task)
                for supertask in self._logic_layer.get_task_system()
                .network_graph()
                .hierarchy_graph()
                .supertasks(self._task)
            ),
            delete_hierarchy=self._logic_layer.delete_task_hierarchy,
            get_task_name=lambda task: self._logic_layer.get_task_system()
            .attributes_register()[task]
            .name,
        )

    def _open_subtask_hierarchy_deletion_window(self) -> None:
        assert self._task is not None

        HierarchyDeletionWindow(
            master=self,
            hierarchy_options=(
                (self._task, subtask)
                for subtask in self._logic_layer.get_task_system()
                .network_graph()
                .hierarchy_graph()
                .subtasks(self._task)
            ),
            delete_hierarchy=self._logic_layer.delete_task_hierarchy,
            get_task_name=lambda task: self._logic_layer.get_task_system()
            .attributes_register()[task]
            .name,
        )

    def _open_dependee_task_dependency_deletion_window(self) -> None:
        assert self._task is not None

        DependencyDeletionWindow(
            master=self,
            dependency_options=sorted(
                (dependee_task, self._task)
                for dependee_task in self._logic_layer.get_task_system()
                .network_graph()
                .dependency_graph()
                .dependee_tasks(self._task)
            ),
            delete_dependency=self._logic_layer.delete_task_dependency,
            get_task_name=lambda task: self._logic_layer.get_task_system()
            .attributes_register()[task]
            .name,
        )

    def _open_dependent_task_dependency_deletion_window(self) -> None:
        assert self._task is not None

        DependencyDeletionWindow(
            master=self,
            dependency_options=sorted(
                (self._task, subtask)
                for subtask in self._logic_layer.get_task_system()
                .network_graph()
                .dependency_graph()
                .dependent_tasks(self._task)
            ),
            delete_dependency=self._logic_layer.delete_task_dependency,
            get_task_name=lambda task: self._logic_layer.get_task_system()
            .attributes_register()[task]
            .name,
        )

    def _create_new_task(self) -> None:
        TaskCreationWindow(master=self, logic_layer=self._logic_layer)

    def _delete_task(self) -> None:
        assert self._task is not None

        TaskDeletionConfirmationWindow(
            master=self,
            task=self._task,
            delete_task=self._logic_layer.delete_task,
            get_task_name=lambda task: self._logic_layer.get_task_system()
            .attributes_register()[task]
            .name,
        )

    def _on_description_scrolled_text_goes_out_of_focus(self) -> None:
        # It's possible to 'focus/unfocus' the description field even when no task is
        # active, so ignore these
        if self._task is None:
            return

        logger.info("Description field lost focus")
        self._save_current_description()

    def _on_closing(self) -> None:
        logger.info("Closing task details window")

        if self._task is not None:
            self._save_current_name()
            self._save_current_description()

        self.winfo_toplevel().destroy()
