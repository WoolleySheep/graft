import functools
import logging
import tkinter as tk
from collections.abc import Generator, Sequence
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import (
    event_broker,
)
from graft.layers.presentation.tkinter_gui.helpers.create_hierarchy_error_windows import (
    convert_create_hierarchy_exceptions_to_error_windows,
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


class LabelledOptionMenu(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        label_text: str,
        variable: tk.StringVar,
        menu_options: Sequence[str],
    ) -> None:
        super().__init__(master=master)

        self._label = ttk.Label(self, text=label_text)
        self._option_menu = ttk.OptionMenu(
            self, variable, menu_options[0] if menu_options else None, *menu_options
        )

        self._label.grid(row=0, column=0)
        self._option_menu.grid(row=0, column=1)


class HierarchyCreationWindow(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        logic_layer: architecture.LogicLayer,
        supertask: tasks.UID | None = None,
        subtask: tasks.UID | None = None,
    ) -> None:
        super().__init__(master=master)
        self._logic_layer = logic_layer
        self._supertask = supertask
        self._subtask = subtask

        self.title("Create hierarchy")

        menu_options = list(_get_menu_options(logic_layer=logic_layer))

        self._selected_supertask = tk.StringVar(self)
        supertask_section = tk.Frame(master=self)
        supertask_label = ttk.Label(master=supertask_section, text="Super-task: ")
        supertask_option_menu = ttk.OptionMenu(
            supertask_section,
            self._selected_supertask,
            menu_options[0] if menu_options else None,
            *menu_options,
        )

        self._selected_subtask = tk.StringVar(self)
        subtask_section = tk.Frame(master=self)
        subtask_label = ttk.Label(master=subtask_section, text="Sub-task: ")
        subtask_option_menu = ttk.OptionMenu(
            subtask_section,
            self._selected_subtask,
            menu_options[0] if menu_options else None,
            *menu_options,
        )

        if self._supertask is not None:
            self._selected_supertask.set(
                _format_task_uid_name_as_menu_option(
                    self._supertask, _get_task_name(logic_layer, self._supertask)
                )
            )
            supertask_option_menu.config(state=tk.DISABLED)

        if self._subtask is not None:
            self._selected_subtask.set(
                _format_task_uid_name_as_menu_option(
                    self._subtask, _get_task_name(logic_layer, self._subtask)
                )
            )
            subtask_option_menu.config(state=tk.DISABLED)

        confirm_button = ttk.Button(
            self,
            text="Confirm",
            command=self._on_confirm_button_clicked,
        )

        supertask_section.grid(row=0, column=0)
        subtask_section.grid(row=1, column=0)
        confirm_button.grid(row=2, column=0)

        supertask_label.grid(row=0, column=0)
        supertask_option_menu.grid(row=0, column=1)

        subtask_label.grid(row=0, column=0)
        subtask_option_menu.grid(row=0, column=1)

    def _on_confirm_button_clicked(self) -> None:
        logger.info("Confirm hierarchy creation button clicked")
        self._create_hierarchy_between_selected_tasks_then_destroy_window()

    def _create_hierarchy_between_selected_tasks_then_destroy_window(self) -> None:
        supertask = self._get_selected_supertask()
        subtask = self._get_selected_subtask()

        if not convert_create_hierarchy_exceptions_to_error_windows(
            functools.partial(
                self._logic_layer.create_task_hierarchy,
                supertask=supertask,
                subtask=subtask,
            ),
            self._logic_layer.get_task_system(),
            master=self,
        ):
            return

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())
        self.destroy()

    def _get_selected_supertask(self) -> tasks.UID:
        return _parse_task_uid_from_menu_option(self._selected_supertask.get())

    def _get_selected_subtask(self) -> tasks.UID:
        return _parse_task_uid_from_menu_option(self._selected_subtask.get())
