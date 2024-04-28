import tkinter as tk
from collections.abc import Generator, Sequence
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.tkinter_gui import event_broker, helpers


def _get_dependencies_with_names(
    logic_layer: architecture.LogicLayer,
) -> Generator[
    tuple[tuple[tasks.UID, tasks.Name | None], tuple[tasks.UID, tasks.Name | None]],
    None,
    None,
]:
    attributes_register = logic_layer.get_task_attributes_register_view()
    for (
        dependee_task,
        dependent_task,
    ) in logic_layer.get_dependency_graph_view().dependencies():
        yield (
            (dependee_task, attributes_register[dependee_task].name),
            (dependent_task, attributes_register[dependent_task].name),
        )


def _format_task_uid_name(task_uid: tasks.UID, task_name: tasks.Name | None) -> str:
    if task_name is None:
        return f"[{task_uid}]"

    return f"[{task_uid}] {task_name}"


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


class DependencyDeletionWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        def delete_dependency_between_selected_tasks_then_destroy_window() -> None:
            dependee_task, dependent_task = _parse_task_uids_from_menu_option(
                self.selected_dependency.get()
            )
            try:
                logic_layer.delete_dependency(dependee_task, dependent_task)
            except Exception as e:
                helpers.UnknownExceptionOperationFailedWindow(master=self, exception=e)
                return
            broker = event_broker.get_singleton()
            broker.publish(event_broker.SystemModified())
            self.destroy()

        super().__init__(master=master)

        self.title("Delete dependency")

        menu_options = list(_get_menu_options(logic_layer=logic_layer))

        self.selected_dependency = tk.StringVar(self)
        self.dependency_option_menu = ttk.OptionMenu(
            self, self.selected_dependency, *menu_options
        )

        self.confirm_button = ttk.Button(
            self,
            text="Confirm",
            command=delete_dependency_between_selected_tasks_then_destroy_window,
        )

        self.dependency_option_menu.grid(row=0, column=0)
        self.confirm_button.grid(row=1, column=0)


def create_dependency_deletion_window(
    master: tk.Misc, logic_layer: architecture.LogicLayer
) -> None:
    DependencyDeletionWindow(master=master, logic_layer=logic_layer)
