import tkinter as tk
from collections.abc import Generator, Sequence
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.tkinter_gui import event_broker


def _get_hierarchies_with_names(logic_layer: architecture.LogicLayer) -> Generator[tuple[tuple[tasks.UID, tasks.Name | None], tuple[tasks.UID, tasks.Name | None]], None, None]:
    attributes_register = logic_layer.get_task_attributes_register_view()
    for supertask, subtask in logic_layer.get_hierarchy_graph_view().hierarchies():
        yield (
            (supertask, attributes_register[supertask].name),
            (subtask, attributes_register[subtask].name),
        )

def _format_task_uid_name(
    task_uid: tasks.UID, task_name: tasks.Name | None
) -> str:
    if task_name is None:
        return f"[{task_uid}]"

    return f"[{task_uid}] {task_name}"


def _get_menu_options(
    logic_layer: architecture.LogicLayer,
) -> Generator[str, None, None]:
    hierarchies_with_names = sorted(
        _get_hierarchies_with_names(logic_layer=logic_layer), key=lambda x: (x[0][0], x[1][0])
    )

    for (supertask, supertask_name), (subtask, subtask_name) in hierarchies_with_names:
        formatted_supertask = _format_task_uid_name(supertask, supertask_name)
        formatted_subtask = _format_task_uid_name(subtask, subtask_name)
        yield f"{formatted_supertask} -> {formatted_subtask}"

def _parse_task_uid_from_formatted_task_uid_name(formatted_task_uid_name: str) -> tasks.UID:
    first_closing_square_bracket = formatted_task_uid_name.find("]")
    uid_number = int(formatted_task_uid_name[1:first_closing_square_bracket])
    return tasks.UID(uid_number)

def _parse_task_uids_from_menu_option(menu_option: str) -> tuple[tasks.UID, tasks.UID]:
    formatted_tasks = menu_option.split(" -> ")
    if len(formatted_tasks) != 2:
        raise ValueError

    formatted_supertask, formatted_subtask = formatted_tasks
    supertask = _parse_task_uid_from_formatted_task_uid_name(formatted_supertask)
    subtask = _parse_task_uid_from_formatted_task_uid_name(formatted_subtask)
    return supertask, subtask



class LabelledOptionMenu(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        label_text: str,
        variable: tk.StringVar,
        menu_options: Sequence[str],
    ) -> None:
        super().__init__(master=master)

        self.label = ttk.Label(self, text=label_text)
        self.option_menu = ttk.OptionMenu(self, variable, *menu_options)

        self.label.grid(row=0, column=0)
        self.option_menu.grid(row=0, column=1)


class HierarchyDeletionWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        def delete_hierarchy_between_selected_tasks_then_destroy_window() -> None:
            supertask, subtask = _parse_task_uids_from_menu_option(self.selected_hierarchy.get())
            logic_layer.delete_hierarchy(supertask, subtask)
            broker = event_broker.get_singleton()
            broker.publish(event_broker.SystemModified())
            self.destroy()

        super().__init__(master=master)

        self.title("Delete hierarchy")

        menu_options = list(_get_menu_options(logic_layer=logic_layer))

        self.selected_hierarchy = tk.StringVar(self)
        self.hierarchy_option_menu = ttk.OptionMenu(self, self.selected_hierarchy, *menu_options)

        self.confirm_button = ttk.Button(
            self,
            text="Confirm",
            command=delete_hierarchy_between_selected_tasks_then_destroy_window,
        )

        self.hierarchy_option_menu.grid(row=0, column=0)
        self.confirm_button.grid(row=1, column=0)


def create_hierarchy_deletion_window(
    master: tk.Misc, logic_layer: architecture.LogicLayer
) -> None:
    HierarchyDeletionWindow(master=master, logic_layer=logic_layer)
