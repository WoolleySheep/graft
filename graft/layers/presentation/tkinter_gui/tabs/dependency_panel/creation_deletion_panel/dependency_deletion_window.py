import logging
import tkinter as tk
from collections.abc import Generator
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import event_broker

logger = logging.getLogger(__name__)


def _get_dependencies_with_names(
    logic_layer: architecture.LogicLayer,
) -> Generator[
    tuple[tuple[tasks.UID, tasks.Name], tuple[tasks.UID, tasks.Name]],
    None,
    None,
]:
    attributes_register = logic_layer.get_task_system().attributes_register()
    for (
        dependee_task,
        dependent_task,
    ) in (
        logic_layer.get_task_system().network_graph().dependency_graph().dependencies()
    ):
        yield (
            (dependee_task, attributes_register[dependee_task].name),
            (dependent_task, attributes_register[dependent_task].name),
        )


def _format_task_uid_name(task_uid: tasks.UID, task_name: tasks.Name) -> str:
    return f"[{task_uid}] {task_name}" if task_name else f"[{task_uid}]"


def _get_menu_options(
    logic_layer: architecture.LogicLayer,
) -> Generator[str, None, None]:
    dependencies_with_names = sorted(
        _get_dependencies_with_names(logic_layer=logic_layer),
        key=lambda x: (x[0][0], x[1][0]),
    )

    for (dependee_task, dependee_task_name), (
        dependent_task,
        dependent_task_name,
    ) in dependencies_with_names:
        formatted_dependee_task = _format_task_uid_name(
            dependee_task, dependee_task_name
        )
        formatted_dependent_task = _format_task_uid_name(
            dependent_task, dependent_task_name
        )
        yield f"{formatted_dependee_task} -> {formatted_dependent_task}"


def _parse_task_uid_from_formatted_task_uid_name(
    formatted_task_uid_name: str,
) -> tasks.UID:
    first_closing_square_bracket = formatted_task_uid_name.find("]")
    uid_number = int(formatted_task_uid_name[1:first_closing_square_bracket])
    return tasks.UID(uid_number)


def _parse_task_uids_from_menu_option(menu_option: str) -> tuple[tasks.UID, tasks.UID]:
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


class DependencyDeletionWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        self._logic_layer = logic_layer
        super().__init__(master=master)

        self.title("Delete dependency")

        menu_options = list(_get_menu_options(logic_layer=logic_layer))

        self._selected_dependency = tk.StringVar(self)
        self._dependency_option_menu = ttk.OptionMenu(
            self,
            self._selected_dependency,
            menu_options[0] if menu_options else None,
            *menu_options,
        )

        self._confirm_button = ttk.Button(
            self,
            text="Confirm",
            command=self._on_confirm_button_clicked,
        )

        self._dependency_option_menu.grid(row=0, column=0)
        self._confirm_button.grid(row=1, column=0)

    def _on_confirm_button_clicked(self) -> None:
        logger.info("Confirm dependency deletion button clicked")
        self._delete_dependency_between_selected_tasks_then_destroy_window()

    def _delete_dependency_between_selected_tasks_then_destroy_window(self) -> None:
        dependee_task, dependent_task = _parse_task_uids_from_menu_option(
            self._selected_dependency.get()
        )
        try:
            self._logic_layer.delete_task_dependency(dependee_task, dependent_task)
        except Exception:
            # TODO: Add error popup. For now, letting it propegate
            raise

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())
        self.destroy()
