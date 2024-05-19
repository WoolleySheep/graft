import tkinter as tk
from collections.abc import Generator
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.tkinter_gui import event_broker, helpers


def _get_task_uids_with_names(
    logic_layer: architecture.LogicLayer,
) -> Generator[tuple[tasks.UID, tasks.Name | None], None, None]:
    """Yield pairs of task UIDs and task names."""
    for uid, attributes in logic_layer.get_task_attributes_register_view().items():
        yield uid, attributes.name


def _format_task_uid_with_name_as_menu_option(
    task_uid: tasks.UID, task_name: tasks.Name | None
) -> str:
    return f"[{task_uid}]" if task_name is None else f"[{task_uid}] {task_name}"


def _get_menu_options(
    logic_layer: architecture.LogicLayer,
) -> Generator[str, None, None]:
    task_uids_names = sorted(
        _get_task_uids_with_names(logic_layer=logic_layer), key=lambda x: x[0]
    )
    for uid, name in task_uids_names:
        yield _format_task_uid_with_name_as_menu_option(uid, name)


def _parse_task_uid_from_menu_option(menu_option: str) -> tasks.UID:
    first_closing_square_bracket = menu_option.find("]")
    uid_number = int(menu_option[1:first_closing_square_bracket])
    return tasks.UID(uid_number)


class TaskDeletionWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        def delete_selected_task_then_destroy_window() -> None:
            uid = _parse_task_uid_from_menu_option(self.selected_task.get())
            try:
                logic_layer.delete_task(uid)
            except tasks.HasSuperTasksError as e:
                system = tasks.System.empty()
                system.add_task(e.task)
                system.set_name(
                    e.task,
                    logic_layer.get_task_attributes_register_view()[e.task].name,
                )
                for supertask in e.supertasks:
                    system.add_task(supertask)
                    system.set_name(
                        supertask,
                        logic_layer.get_task_attributes_register_view()[supertask].name,
                    )
                    system.add_hierarchy(supertask, e.task)

                helpers.HierarchyGraphOperationFailedWindow(
                    master=self,
                    text="Cannot delete task as it has supertask(s)",
                    system=system,
                    highlighted_tasks={e.task},
                )
                return
            except tasks.HasSubTasksError as e:
                system = tasks.System.empty()
                system.add_task(e.task)
                system.set_name(
                    e.task,
                    logic_layer.get_task_attributes_register_view()[e.task].name,
                )
                for subtask in e.subtasks:
                    system.add_task(subtask)
                    system.set_name(
                        subtask,
                        logic_layer.get_task_attributes_register_view()[subtask].name,
                    )
                    system.add_hierarchy(e.task, subtask)

                helpers.HierarchyGraphOperationFailedWindow(
                    master=self,
                    text="Cannot delete task as it has subtask(s)",
                    system=system,
                    highlighted_tasks={e.task},
                )
                return
            except tasks.HasDependeeTasksError as e:
                system = tasks.System.empty()
                system.add_task(e.task)
                system.set_name(
                    uid, logic_layer.get_task_attributes_register_view()[e.task].name
                )
                for dependee_task in e.dependee_tasks:
                    system.add_task(dependee_task)
                    system.set_name(
                        dependee_task,
                        logic_layer.get_task_attributes_register_view()[
                            dependee_task
                        ].name,
                    )
                    system.add_dependency(dependee_task, e.task)

                helpers.DependencyGraphOperationFailedWindow(
                    master=self,
                    text="Cannot delete task as it has dependee-tasks",
                    system=system,
                    highlighted_tasks={e.task},
                )
                return
            except tasks.HasDependentTasksError as e:
                system = tasks.System.empty()
                system.add_task(e.task)
                system.set_name(
                    e.task,
                    logic_layer.get_task_attributes_register_view()[e.task].name,
                )
                for dependent_task in e.dependent_tasks:
                    system.add_task(dependent_task)
                    system.set_name(
                        dependent_task,
                        logic_layer.get_task_attributes_register_view()[
                            dependent_task
                        ].name,
                    )
                    system.add_dependency(e.task, dependent_task)

                helpers.DependencyGraphOperationFailedWindow(
                    master=self,
                    text="Cannot delete task as it has dependent-tasks",
                    system=system,
                    highlighted_tasks={e.task},
                )
                return
            except Exception as e:
                helpers.UnknownExceptionOperationFailedWindow(master=self, exception=e)
                return
            broker = event_broker.get_singleton()
            broker.publish(event_broker.SystemModified())
            self.destroy()

        super().__init__(master=master)

        self.title("Delete task")

        self.selected_task = tk.StringVar(self)
        menu_options = list(_get_menu_options(logic_layer=logic_layer))
        self.task_selection = ttk.OptionMenu(
            self,
            self.selected_task,
            menu_options[0] if menu_options else None,
            *menu_options,
        )

        self.confirm_button = ttk.Button(
            self, text="Confirm", command=delete_selected_task_then_destroy_window
        )

        self.task_selection.grid(row=0, column=0)
        self.confirm_button.grid(row=1, column=0)


def create_task_deletion_window(
    master: tk.Misc, logic_layer: architecture.LogicLayer
) -> None:
    TaskDeletionWindow(master=master, logic_layer=logic_layer)
