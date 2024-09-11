import logging
import tkinter as tk
from collections.abc import Generator, Sequence
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.layers.display.tkinter_gui import event_broker, helpers
from graft.layers.display.tkinter_gui.helpers import format_task_name_for_annotation

logger = logging.getLogger(__name__)


def _get_task_uids_names(
    logic_layer: architecture.LogicLayer,
) -> Generator[tuple[tasks.UID, tasks.Name], None, None]:
    """Yield pairs of task UIDs and task names."""
    for uid, attributes in logic_layer.get_task_system().attributes_register().items():
        yield uid, attributes.name


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


class DependencyCreationWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        self._logic_layer = logic_layer
        super().__init__(master=master)

        self.title("Create dependency")

        menu_options = list(_get_menu_options(logic_layer=logic_layer))

        self._selected_dependee_task = tk.StringVar(self)
        self._dependee_task_option_menu = LabelledOptionMenu(
            self,
            label_text="Dependee-task: ",
            variable=self._selected_dependee_task,
            menu_options=menu_options,
        )

        self._selected_dependent_task = tk.StringVar(self)
        self._dependent_task_option_menu = LabelledOptionMenu(
            self,
            label_text="Dependent-task: ",
            variable=self._selected_dependent_task,
            menu_options=menu_options,
        )

        self._confirm_button = ttk.Button(
            self,
            text="Confirm",
            command=self._on_confirm_button_clicked,
        )

        self._dependee_task_option_menu.grid(row=0, column=0)
        self._dependent_task_option_menu.grid(row=1, column=0)
        self._confirm_button.grid(row=2, column=0)

    def _on_confirm_button_clicked(self) -> None:
        logger.info("Confirm dependency creation button clicked")
        self._create_dependency_between_selected_tasks_then_destroy_window()

    def _create_dependency_between_selected_tasks_then_destroy_window(self) -> None:
        dependee_task = _parse_task_uid_from_menu_option(
            self._selected_dependee_task.get()
        )
        dependent_task = _parse_task_uid_from_menu_option(
            self._selected_dependent_task.get()
        )
        try:
            self._logic_layer.create_task_dependency(dependee_task, dependent_task)
        except tasks.DependencyLoopError as e:
            dependency_graph = tasks.DependencyGraph()
            dependency_graph.add_task(e.task)
            helpers.DependencyGraphOperationFailedWindow(
                master=self,
                description_text="Cannot create a dependency between a task and itself",
                dependency_graph=dependency_graph,
                get_task_annotation_text=lambda task: format_task_name_for_annotation(
                    self._logic_layer.get_task_system().attributes_register()[task].name
                ),
                highlighted_tasks={e.task},
                additional_dependencies={(e.task, e.task)},
            )
            return
        except tasks.DependencyAlreadyExistsError as e:
            dependency_graph = tasks.DependencyGraph()
            for task in [e.dependent_task, e.dependee_task]:
                dependency_graph.add_task(task)
            dependency_graph.add_dependency(e.dependee_task, e.dependent_task)
            helpers.DependencyGraphOperationFailedWindow(
                master=self,
                description_text="Dependency already exists",
                dependency_graph=dependency_graph,
                get_task_annotation_text=lambda task: format_task_name_for_annotation(
                    self._logic_layer.get_task_system().attributes_register()[task].name
                ),
                additional_dependencies={(e.dependent_task, e.dependee_task)},
            )
            return
        except tasks.DependencyIntroducesCycleError as e:
            helpers.DependencyGraphOperationFailedWindow(
                master=self,
                description_text="Introduces dependency cycle",
                dependency_graph=e.connecting_subgraph,
                get_task_annotation_text=lambda task: format_task_name_for_annotation(
                    self._logic_layer.get_task_system().attributes_register()[task].name
                ),
                highlighted_tasks={e.dependee_task, e.dependent_task},
                additional_dependencies={(e.dependee_task, e.dependent_task)},
            )
            return
        except Exception:
            # TODO: Add error popup. For now, letting it propegate
            raise

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())
        self.destroy()
