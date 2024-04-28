import tkinter as tk
from collections.abc import Generator, Sequence
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.tkinter_gui import event_broker, helpers


def _get_task_uids_names(
    logic_layer: architecture.LogicLayer,
) -> Generator[tuple[tasks.UID, tasks.Name | None], None, None]:
    """Yield pairs of task UIDs and task names."""
    for uid, attributes in logic_layer.get_task_attributes_register_view().items():
        yield uid, attributes.name


def _format_task_uid_name_as_menu_option(
    task_uid: tasks.UID, task_name: tasks.Name | None
) -> str:
    if task_name is None:
        return f"[{task_uid}]"

    return f"[{task_uid}] {task_name}"


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

        self.label = ttk.Label(self, text=label_text)
        self.option_menu = ttk.OptionMenu(self, variable, *menu_options)

        self.label.grid(row=0, column=0)
        self.option_menu.grid(row=0, column=1)


class HierarchyCreationWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        def create_hierarchy_between_selected_tasks_then_destroy_window() -> None:
            supertask = _parse_task_uid_from_menu_option(self.selected_supertask.get())
            subtask = _parse_task_uid_from_menu_option(self.selected_subtask.get())
            try:
                logic_layer.create_hierarchy(supertask, subtask)
            except tasks.HierarchyLoopError as e:
                system = tasks.System.empty()
                system.add_task(e.task)
                helpers.SingleHierarchyGraphOperationFailedWindow(
                    master=self, text=str(e), system=system
                )
                return
            except Exception as e:
                helpers.UnknownExceptionOperationFailedWindow(self, exception=e)
                return

            broker = event_broker.get_singleton()
            broker.publish(event_broker.SystemModified())
            self.destroy()

        super().__init__(master=master)

        self.title("Create hierarchy")

        menu_options = list(_get_menu_options(logic_layer=logic_layer))

        self.selected_supertask = tk.StringVar(self)
        self.supertask_option_menu = LabelledOptionMenu(
            self,
            label_text="Super-task: ",
            variable=self.selected_supertask,
            menu_options=menu_options,
        )

        self.selected_subtask = tk.StringVar(self)
        self.subtask_option_menu = LabelledOptionMenu(
            self,
            label_text="Sub-task: ",
            variable=self.selected_subtask,
            menu_options=menu_options,
        )

        self.confirm_button = ttk.Button(
            self,
            text="Confirm",
            command=create_hierarchy_between_selected_tasks_then_destroy_window,
        )

        self.supertask_option_menu.grid(row=0, column=0)
        self.subtask_option_menu.grid(row=1, column=0)
        self.confirm_button.grid(row=2, column=0)
