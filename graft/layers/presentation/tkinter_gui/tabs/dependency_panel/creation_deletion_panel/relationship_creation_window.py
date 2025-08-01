import logging
import tkinter as tk
from collections.abc import Callable, Iterable
from tkinter import ttk
from typing import Final

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import (
    event_broker,
)

logger = logging.getLogger(__name__)

_NO_TASK_MENU_OPTION: Final = ""


def _format_task_uid_name_as_menu_option(
    task_uid: tasks.UID, task_name: tasks.Name
) -> str:
    return f"[{task_uid}] {task_name}" if task_name else f"[{task_uid}]"


def _get_menu_options(
    tasks_: Iterable[tasks.UID],
    get_task_name: Callable[[tasks.UID], tasks.Name],
) -> list[str]:
    return [
        _format_task_uid_name_as_menu_option(task, get_task_name(task))
        for task in sorted(tasks_)
    ]


def _parse_task_uid_from_menu_option(menu_option: str) -> tasks.UID:
    first_closing_square_bracket = menu_option.find("]")
    uid_number = int(menu_option[1:first_closing_square_bracket])
    return tasks.UID(uid_number)


class RelationshipCreationWindow(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        title: str,
        source_label_text: str,
        target_label_text: str,
        get_tasks: Callable[[], Iterable[tasks.UID]],
        get_incomplete_tasks: Callable[[], Iterable[tasks.UID]],
        get_task_name: Callable[[tasks.UID], tasks.Name],
        create_relationship: Callable[[tasks.UID, tasks.UID], bool],
        fixed_source: tasks.UID | None = None,
        fixed_target: tasks.UID | None = None,
    ) -> None:
        super().__init__(master=master)
        self._get_tasks = get_tasks
        self._get_incomplete_tasks = get_incomplete_tasks
        self._get_task_name = get_task_name
        self._create_relationship = create_relationship
        self._fixed_source = fixed_source
        self._fixed_target = fixed_target

        self.title(title)

        self._selected_source = tk.StringVar(self)
        source_label = ttk.Label(master=self, text=source_label_text)
        self._source_option_menu = ttk.Combobox(
            master=self,
            textvariable=self._selected_source,
            values=[],
            state="readonly",
        )
        if self._fixed_source is not None:
            self._selected_source.set(
                _format_task_uid_name_as_menu_option(
                    self._fixed_source,
                    self._get_task_name(self._fixed_source),
                )
            )
            self._source_option_menu.config(state=tk.DISABLED)

        self._selected_target = tk.StringVar(self)
        target_label = ttk.Label(master=self, text=target_label_text)
        self._target_option_menu = ttk.Combobox(
            master=self,
            textvariable=self._selected_target,
            values=[],
            state="readonly",
        )
        if self._fixed_target is not None:
            self._selected_target.set(
                _format_task_uid_name_as_menu_option(
                    self._fixed_target,
                    self._get_task_name(self._fixed_target),
                )
            )
            self._target_option_menu.config(state=tk.DISABLED)

        self._show_completed_tasks = tk.BooleanVar()
        show_completed_tasks_checkbutton = ttk.Checkbutton(
            master=self,
            text="Show completed tasks",
            variable=self._show_completed_tasks,
            command=self._update_task_option_menus,
        )
        self._show_completed_tasks.set(False)

        self._confirm_button = ttk.Button(
            self,
            text="Confirm",
            command=self._on_confirm_button_clicked,
        )

        self._selected_source.trace_add(
            "write", lambda _, __, ___: self._update_confirm_button_state()
        )
        self._selected_target.trace_add(
            "write", lambda _, __, ___: self._update_confirm_button_state()
        )

        self._update_task_option_menus()
        self._update_confirm_button_state()

        source_label.grid(row=0, column=0)
        self._source_option_menu.grid(row=0, column=1)
        target_label.grid(row=1, column=0)
        self._target_option_menu.grid(row=1, column=1)
        show_completed_tasks_checkbutton.grid(row=0, column=2, rowspan=2)
        self._confirm_button.grid(row=3, column=0, columnspan=2)

    def _update_task_option_menus(self) -> None:
        self._update_source_option_menu()
        self._update_target_option_menu()

    def _update_source_option_menu(self) -> None:
        if self._fixed_source is not None:
            return

        tasks = list(
            self._get_tasks()
            if self._show_completed_tasks.get()
            else self._get_incomplete_tasks()
        )

        self._source_option_menu["values"] = _get_menu_options(
            tasks, self._get_task_name
        )

        if (
            selected_source := self._get_selected_source()
        ) is not None and selected_source not in tasks:
            self._selected_source.set(_NO_TASK_MENU_OPTION)

    def _update_target_option_menu(self) -> None:
        if self._fixed_target is not None:
            return

        tasks = list(
            self._get_tasks()
            if self._show_completed_tasks.get()
            else self._get_incomplete_tasks()
        )

        self._target_option_menu["values"] = _get_menu_options(
            tasks, self._get_task_name
        )

        if (
            selected_target := self._get_selected_target()
        ) is not None and selected_target not in tasks:
            self._selected_target.set(_NO_TASK_MENU_OPTION)

    def _on_confirm_button_clicked(self) -> None:
        logger.info("Confirm relationship creation button clicked")
        self._create_relationship_between_selected_tasks_then_destroy_window()

    def _create_relationship_between_selected_tasks_then_destroy_window(self) -> None:
        source = self._get_selected_source()
        target = self._get_selected_target()

        assert source is not None
        assert target is not None

        if not self._create_relationship(source, target):
            return

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())
        self.destroy()

    def _get_selected_source(self) -> tasks.UID | None:
        if self._fixed_source is not None:
            return self._fixed_source

        if self._selected_source.get() == _NO_TASK_MENU_OPTION:
            return None

        return _parse_task_uid_from_menu_option(self._selected_source.get())

    def _get_selected_target(self) -> tasks.UID | None:
        if self._fixed_target is not None:
            return self._fixed_target

        if self._selected_target.get() == _NO_TASK_MENU_OPTION:
            return None

        return _parse_task_uid_from_menu_option(self._selected_target.get())

    def _on_show_completed_tasks_button_toggled(self) -> None:
        self._update_task_option_menus()

    def _update_confirm_button_state(self) -> None:
        self._confirm_button.config(
            state=tk.NORMAL
            if self._get_selected_source() is not None
            and self._get_selected_target() is not None
            else tk.DISABLED
        )
