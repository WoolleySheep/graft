import tkinter as tk
from collections.abc import Generator
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.tkinter_gui import event_broker


def _get_task_uids_names(
    logic_layer: architecture.LogicLayer,
) -> Generator[tuple[tasks.UID, tasks.Name | None], None, None]:
    """Yield pairs of task UIDs and task names, sorted by uid."""
    for uid, attributes in logic_layer.get_task_attributes_register_view().items():
        yield uid, attributes.name


def format_task_uid_name_for_option_menu(
    task_uid: tasks.UID, task_name: tasks.Name | None
) -> str:
    if task_name is None:
        return f"[{task_uid}]"
    else:
        return f"[{task_uid}] {task_name}"


def _get_get_menu_options(
    logic_layer: architecture.LogicLayer,
) -> Generator[str, None, None]:
    task_uids_names = sorted(
        _get_task_uids_names(logic_layer=logic_layer), key=lambda x: x[0]
    )
    for uid, name in task_uids_names:
        yield format_task_uid_name_for_option_menu(uid, name)


def _parse_task_uid_from_menu_option(menu_option: str) -> tasks.UID:
    first_closing_square_bracket = menu_option.find("]")
    uid_number = int(menu_option[1:first_closing_square_bracket])
    return tasks.UID(uid_number)


class TaskDeletionWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        def delete_selected_task_then_destroy_window() -> None:
            uid = _parse_task_uid_from_menu_option(self.selected_task.get())
            logic_layer.delete_task(uid)
            broker = event_broker.get_singleton()
            broker.publish(event_broker.SystemModified())
            self.destroy()

        super().__init__(master=master)

        self.title("Create task")

        self.selected_task = tk.StringVar(self)
        self.task_selection = ttk.OptionMenu(
            self,
            self.selected_task,
            *_get_get_menu_options(logic_layer=logic_layer),
        )

        self.confirm_button = ttk.Button(
            self, text="Confirm", command=delete_selected_task_then_destroy_window
        )

        self.task_selection.grid(row=0)
        self.confirm_button.grid(row=1)


def create_task_deletion_window(
    master: tk.Misc, logic_layer: architecture.LogicLayer
) -> None:
    TaskDeletionWindow(master=master, logic_layer=logic_layer)
