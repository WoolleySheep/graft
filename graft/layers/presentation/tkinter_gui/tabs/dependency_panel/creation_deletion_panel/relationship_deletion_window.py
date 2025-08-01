import logging
import tkinter as tk
from collections.abc import Callable, Iterable
from tkinter import ttk
from typing import Final

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import event_broker

_NO_TASK_MENU_OPTION: Final = ""

logger: Final = logging.getLogger(__name__)


def _format_task_uid_name(task_uid: tasks.UID, task_name: tasks.Name) -> str:
    return f"[{task_uid}] {task_name}" if task_name else f"[{task_uid}]"


def _format_relationship_menu_option(
    source: tasks.UID,
    target: tasks.UID,
    get_task_name: Callable[[tasks.UID], tasks.Name],
) -> str:
    dependee_task_name = get_task_name(source)
    dependent_task_name = get_task_name(target)
    formatted_source = _format_task_uid_name(source, dependee_task_name)
    formatted_target = _format_task_uid_name(target, dependent_task_name)
    return f"{formatted_source} -> {formatted_target}"


def _parse_task_uid_from_formatted_task_uid_name(
    formatted_task_uid_name: str,
) -> tasks.UID:
    first_closing_square_bracket = formatted_task_uid_name.find("]")
    uid_number = int(formatted_task_uid_name[1:first_closing_square_bracket])
    return tasks.UID(uid_number)


def _parse_relationship_from_menu_option(
    menu_option: str,
) -> tuple[tasks.UID, tasks.UID]:
    formatted_tasks = menu_option.split(" -> ")
    if len(formatted_tasks) != 2:
        raise ValueError

    formatted_dependee_task, formatted_dependent_task = formatted_tasks
    dependee_task = _parse_task_uid_from_formatted_task_uid_name(
        formatted_dependee_task
    )
    dependent_task = _parse_task_uid_from_formatted_task_uid_name(
        formatted_dependent_task
    )
    return dependee_task, dependent_task


class RelationshipDeletionWindow(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        title: str,
        relationship_options: Iterable[tuple[tasks.UID, tasks.UID]],
        delete_relationship: Callable[[tasks.UID, tasks.UID], bool],
        get_task_name: Callable[[tasks.UID], tasks.Name],
    ) -> None:
        super().__init__(master=master)
        self._delete_relationship = delete_relationship
        self._get_task_name = get_task_name

        self.title(title)

        menu_options = [
            _format_relationship_menu_option(
                source,
                target,
                get_task_name,
            )
            for source, target in sorted(relationship_options)
        ]

        self._selected_relationship = tk.StringVar(self)
        self._relationship_options_menu = ttk.Combobox(
            master=self,
            textvariable=self._selected_relationship,
            values=menu_options,
            state="readonly",
        )
        self._selected_relationship.set(_NO_TASK_MENU_OPTION)

        self._confirm_button = ttk.Button(
            self,
            text="Confirm",
            command=self._on_confirm_button_clicked,
        )

        self._update_confirm_button_state()

        self._selected_relationship.trace_add(
            "write", lambda _, __, ___: self._update_confirm_button_state()
        )

        self._relationship_options_menu.grid(row=0, column=0)
        self._confirm_button.grid(row=1, column=0)

    def _on_confirm_button_clicked(self) -> None:
        self._delete_releationship_between_selected_tasks_then_destroy_window()

    def _get_selected_relationship(self) -> tuple[tasks.UID, tasks.UID] | None:
        if self._selected_relationship.get() == _NO_TASK_MENU_OPTION:
            return None

        return _parse_relationship_from_menu_option(self._selected_relationship.get())

    def _delete_releationship_between_selected_tasks_then_destroy_window(self) -> None:
        relationship = self._get_selected_relationship()
        assert relationship is not None

        dependee_task, dependent_task = relationship

        if not self._delete_relationship(dependee_task, dependent_task):
            return

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())
        self.destroy()

    def _update_confirm_button_state(self) -> None:
        self._confirm_button["state"] = (
            tk.NORMAL if self._get_selected_relationship() is not None else tk.DISABLED
        )
