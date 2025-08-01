import functools
import logging
import tkinter as tk
from collections.abc import Generator
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import (
    event_broker,
)
from graft.layers.presentation.tkinter_gui.helpers.create_dependency_error_windows import (
    convert_create_dependency_exceptions_to_error_windows,
)

logger = logging.getLogger(__name__)


def _get_task_uids_names(
    logic_layer: architecture.LogicLayer,
) -> Generator[tuple[tasks.UID, tasks.Name], None, None]:
    """Yield pairs of task UIDs and task names."""
    for uid, attributes in logic_layer.get_task_system().attributes_register().items():
        yield uid, attributes.name


def _get_task_name(
    logic_layer: architecture.LogicLayer, task_uid: tasks.UID
) -> tasks.Name:
    return logic_layer.get_task_system().attributes_register()[task_uid].name


def _format_task_uid_name_as_menu_option(
    task_uid: tasks.UID, task_name: tasks.Name
) -> str:
    return f"[{task_uid}] {task_name}" if task_name else f"[{task_uid}]"


def _get_menu_options(
    logic_layer: architecture.LogicLayer,
) -> Generator[str, None, None]:
    task_uids_names = sorted(
        _get_task_uids_names(logic_layer=logic_layer), key=lambda x: x[0]
    )
    for uid, name in task_uids_names:
        yield _format_task_uid_name_as_menu_option(uid, name)


def _parse_task_uid_from_menu_option(menu_option: str) -> tasks.UID:
    first_closing_square_bracket = menu_option.find("]")
    uid_number = int(menu_option[1:first_closing_square_bracket])
    return tasks.UID(uid_number)


class DependencyCreationWindow(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        logic_layer: architecture.LogicLayer,
        dependee_task: tasks.UID | None = None,
        dependent_task: tasks.UID | None = None,
    ) -> None:
        super().__init__(master=master)
        self._logic_layer = logic_layer
        self._dependee_task = dependee_task
        self._dependent_task = dependent_task

        self.title("Create dependency")

        menu_options = list(_get_menu_options(logic_layer=logic_layer))

        self._selected_dependee_task = tk.StringVar(self)
        dependee_task_section = tk.Frame(master=self)
        dependee_task_label = ttk.Label(
            master=dependee_task_section, text="Dependee-task: "
        )
        dependee_task_option_menu = ttk.OptionMenu(
            dependee_task_section,
            self._selected_dependee_task,
            menu_options[0] if menu_options else None,
            *menu_options,
        )

        self._selected_dependent_task = tk.StringVar(self)
        dependent_task_section = tk.Frame(master=self)
        dependent_task_label = ttk.Label(
            master=dependent_task_section, text="Dependent-task: "
        )
        dependent_task_option_menu = ttk.OptionMenu(
            dependent_task_section,
            self._selected_dependent_task,
            menu_options[0] if menu_options else None,
            *menu_options,
        )

        if self._dependee_task is not None:
            self._selected_dependee_task.set(
                _format_task_uid_name_as_menu_option(
                    self._dependee_task,
                    _get_task_name(logic_layer, self._dependee_task),
                )
            )
            dependee_task_option_menu.config(state=tk.DISABLED)

        if self._dependent_task is not None:
            self._selected_dependent_task.set(
                _format_task_uid_name_as_menu_option(
                    self._dependent_task,
                    _get_task_name(logic_layer, self._dependent_task),
                )
            )
            dependent_task_option_menu.config(state=tk.DISABLED)

        confirm_button = ttk.Button(
            self,
            text="Confirm",
            command=self._on_confirm_button_clicked,
        )

        dependee_task_section.grid(row=0, column=0)
        dependent_task_section.grid(row=1, column=0)
        confirm_button.grid(row=2, column=0)

        dependee_task_label.grid(row=0, column=0)
        dependee_task_option_menu.grid(row=0, column=1)

        dependent_task_label.grid(row=0, column=0)
        dependent_task_option_menu.grid(row=0, column=1)

    def _on_confirm_button_clicked(self) -> None:
        logger.info("Confirm dependency creation button clicked")
        self._create_dependency_between_selected_tasks_then_destroy_window()

    def _get_selected_dependee_task(self) -> tasks.UID:
        return _parse_task_uid_from_menu_option(self._selected_dependee_task.get())

    def _get_selected_dependent_task(self) -> tasks.UID:
        return _parse_task_uid_from_menu_option(self._selected_dependent_task.get())

    def _create_dependency_between_selected_tasks_then_destroy_window(self) -> None:
        dependee_task = self._get_selected_dependee_task()
        dependent_task = self._get_selected_dependent_task()

        if not convert_create_dependency_exceptions_to_error_windows(
            functools.partial(
                self._logic_layer.create_task_dependency,
                dependee_task=dependee_task,
                dependent_task=dependent_task,
            ),
            self._logic_layer.get_task_system(),
            master=self,
        ):
            return

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())
        self.destroy()
