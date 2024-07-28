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
    for uid, attributes in logic_layer.get_task_system().attributes_register().items():
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
        self.option_menu = ttk.OptionMenu(
            self, variable, menu_options[0] if menu_options else None, *menu_options
        )

        self.label.grid(row=0, column=0)
        self.option_menu.grid(row=0, column=1)


class HierarchyCreationWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        def create_hierarchy_between_selected_tasks_then_destroy_window() -> None:
            supertask = self._get_selected_supertask()
            subtask = self._get_selected_subtask()
            try:
                self.logic_layer.create_task_hierarchy(supertask, subtask)
            except tasks.HierarchyLoopError as e:
                system = tasks.System.empty()
                system.add_task(e.task)
                system.set_name(
                    e.task,
                    self.logic_layer.get_task_system()
                    .attributes_register()[e.task]
                    .name,
                )
                helpers.HierarchyGraphOperationFailedWindow(
                    master=self,
                    text="Cannot create a hierarchy between a task and itself",
                    system=system,
                    highlighted_tasks={e.task},
                    additional_hierarchies={(e.task, e.task)},
                )
                return
            except tasks.HierarchyAlreadyExistsError as e:
                system = tasks.System.empty()
                for task in [e.subtask, e.supertask]:
                    system.add_task(task)
                    system.set_name(
                        task,
                        self.logic_layer.get_task_system()
                        .attributes_register()[task]
                        .name,
                    )
                system.add_hierarchy(e.supertask, e.subtask)
                helpers.HierarchyGraphOperationFailedWindow(
                    master=self,
                    text="Hierarchy already exists",
                    system=system,
                    highlighted_hierarchies={(e.supertask, e.subtask)},
                )
                return
            except tasks.HierarchyIntroducesCycleError as e:
                system = tasks.System.empty()
                for task in e.connecting_subgraph:
                    system.add_task(task)
                    system.set_name(
                        task,
                        self.logic_layer.get_task_system()
                        .attributes_register()[task]
                        .name,
                    )
                for supertask, subtask in e.connecting_subgraph.hierarchies():
                    system.add_hierarchy(supertask, subtask)
                helpers.HierarchyGraphOperationFailedWindow(
                    master=self,
                    text="Introduces hierarchy cycle",
                    system=system,
                    additional_hierarchies=[(e.supertask, e.subtask)],
                )
                return
            except tasks.HierarchyIntroducesRedundantHierarchyError as e:
                system = tasks.System.empty()
                for task in e.connecting_subgraph:
                    system.add_task(task)
                    system.set_name(
                        task,
                        self.logic_layer.get_task_system()
                        .attributes_register()[task]
                        .name,
                    )
                for supertask, subtask in e.connecting_subgraph.hierarchies():
                    system.add_hierarchy(supertask, subtask)
                helpers.HierarchyGraphOperationFailedWindow(
                    master=self,
                    text="Introduces redundant hierarchy",
                    system=system,
                    additional_hierarchies=[(e.supertask, e.subtask)],
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
        self.logic_layer = logic_layer

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

    def _get_selected_supertask(self) -> tasks.UID:
        return _parse_task_uid_from_menu_option(self.selected_supertask.get())

    def _get_selected_subtask(self) -> tasks.UID:
        return _parse_task_uid_from_menu_option(self.selected_subtask.get())
