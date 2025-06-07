import logging
import tkinter as tk
from collections.abc import Generator, Sequence
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import event_broker, helpers
from graft.layers.presentation.tkinter_gui.helpers import (
    format_task_name_for_annotation,
)

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


class HierarchyCreationWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        self._logic_layer = logic_layer
        super().__init__(master=master)

        self.title("Create hierarchy")

        menu_options = list(_get_menu_options(logic_layer=logic_layer))

        self._selected_supertask = tk.StringVar(self)
        self._supertask_option_menu = LabelledOptionMenu(
            self,
            label_text="Super-task: ",
            variable=self._selected_supertask,
            menu_options=menu_options,
        )

        self._selected_subtask = tk.StringVar(self)
        self._subtask_option_menu = LabelledOptionMenu(
            self,
            label_text="Sub-task: ",
            variable=self._selected_subtask,
            menu_options=menu_options,
        )

        self._confirm_button = ttk.Button(
            self,
            text="Confirm",
            command=self._on_confirm_button_clicked,
        )

        self._supertask_option_menu.grid(row=0, column=0)
        self._subtask_option_menu.grid(row=1, column=0)
        self._confirm_button.grid(row=2, column=0)

    def _on_confirm_button_clicked(self) -> None:
        logger.info("Confirm hierarchy creation button clicked")
        self._create_hierarchy_between_selected_tasks_then_destroy_window()

    def _create_hierarchy_between_selected_tasks_then_destroy_window(self) -> None:
        supertask = self._get_selected_supertask()
        subtask = self._get_selected_subtask()
        try:
            self._logic_layer.create_task_hierarchy(supertask, subtask)
        except tasks.HierarchyLoopError as e:
            hierarchy_graph = tasks.HierarchyGraph()
            hierarchy_graph.add_task(e.task)
            helpers.HierarchyGraphOperationFailedWindow(
                master=self,
                description_text="Cannot create a hierarchy between a task and itself",
                hierarchy_graph=hierarchy_graph,
                get_task_annotation_text=lambda task: format_task_name_for_annotation(
                    self._logic_layer.get_task_system().attributes_register()[task].name
                ),
                highlighted_tasks={e.task},
                additional_hierarchies={(e.task, e.task)},
            )
            return
        except tasks.HierarchyAlreadyExistsError as e:
            hierarchy_graph = tasks.HierarchyGraph()
            for task in [e.subtask, e.supertask]:
                hierarchy_graph.add_task(task)
            hierarchy_graph.add_hierarchy(e.supertask, e.subtask)
            helpers.HierarchyGraphOperationFailedWindow(
                master=self,
                description_text="Hierarchy already exists",
                hierarchy_graph=hierarchy_graph,
                get_task_annotation_text=lambda task: format_task_name_for_annotation(
                    self._logic_layer.get_task_system().attributes_register()[task].name
                ),
                additional_hierarchies={(e.subtask, e.supertask)},
            )
            return
        except tasks.HierarchyIntroducesCycleError as e:
            helpers.HierarchyGraphOperationFailedWindow(
                master=self,
                description_text="Introduces hierarchy cycle",
                hierarchy_graph=e.connecting_subgraph,
                get_task_annotation_text=lambda task: format_task_name_for_annotation(
                    self._logic_layer.get_task_system().attributes_register()[task].name
                ),
                highlighted_tasks={e.supertask, e.subtask},
                additional_hierarchies={(e.supertask, e.subtask)},
            )
            return
        except tasks.HierarchyIntroducesRedundantHierarchyError as e:
            helpers.HierarchyGraphOperationFailedWindow(
                master=self,
                description_text="Introduces redundant hierarchy",
                hierarchy_graph=e.connecting_subgraph,
                get_task_annotation_text=lambda task: format_task_name_for_annotation(
                    self._logic_layer.get_task_system().attributes_register()[task].name
                ),
                additional_hierarchies={(e.supertask, e.subtask)},
            )
            return
        except tasks.HierarchyIntroducesNetworkCycleError as e:
            helpers.NetworkGraphOperationFailedWindow(
                master=self,
                description_text="Introduces network cycle",
                task_network=e.connecting_subgraph,
                get_task_annotation_text=lambda task: format_task_name_for_annotation(
                    self._logic_layer.get_task_system().attributes_register()[task].name
                ),
                highlighted_tasks={e.supertask, e.subtask},
                additional_hierarchies={(e.supertask, e.subtask)},
            )
            return
        except tasks.HierarchyIntroducesDependencyDuplicationError as e:
            helpers.NetworkGraphOperationFailedWindow(
                master=self,
                description_text="Introduces dependency duplication",
                task_network=e.connecting_subgraph,
                get_task_annotation_text=lambda task: format_task_name_for_annotation(
                    self._logic_layer.get_task_system().attributes_register()[task].name
                ),
                additional_hierarchies={(e.supertask, e.subtask)},
            )
            return
        except tasks.HierarchyIntroducesDependencyCrossoverError as e:
            helpers.NetworkGraphOperationFailedWindow(
                master=self,
                description_text="Introduces dependency crossover",
                task_network=e.connecting_subgraph,
                get_task_annotation_text=lambda task: format_task_name_for_annotation(
                    self._logic_layer.get_task_system().attributes_register()[task].name
                ),
                additional_hierarchies={(e.supertask, e.subtask)},
            )
            return

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())
        self.destroy()

    def _get_selected_supertask(self) -> tasks.UID:
        return _parse_task_uid_from_menu_option(self._selected_supertask.get())

    def _get_selected_subtask(self) -> tasks.UID:
        return _parse_task_uid_from_menu_option(self._selected_subtask.get())
