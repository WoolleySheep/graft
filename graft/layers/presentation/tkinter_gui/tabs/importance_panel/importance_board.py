import dataclasses
import enum
import itertools
import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.domain.tasks.importance import Importance
from graft.layers.presentation.tkinter_gui import domain_visual_language, event_broker
from graft.layers.presentation.tkinter_gui.helpers import TaskTableWithName
from graft.layers.presentation.tkinter_gui.helpers.colour import GREY

_IMPORTANCE_TASK_TABLES_ID_COLUMN_WIDTH_PIXELS = 30
_IMPORTANCE_TASK_TABLES_NAME_COLUMN_WIDTH_PIXELS = 200
_IMPORTANCE_TASK_TABLES_NUMBER_OF_DISPLAYED_ROWS = 5


class ImportanceType(enum.Enum):
    INFERRED = (
        enum.auto()
    )  # Task's importance is dependent upon supertasks' importances
    EXPLICIT = enum.auto()  # Task has its own importance


def _create_importance_task_table(master: tk.Misc) -> TaskTableWithName:
    return TaskTableWithName(
        master=master,
        id_column_width_pixels=_IMPORTANCE_TASK_TABLES_ID_COLUMN_WIDTH_PIXELS,
        name_column_width_pixels=_IMPORTANCE_TASK_TABLES_NAME_COLUMN_WIDTH_PIXELS,
        number_of_rows_displayed=_IMPORTANCE_TASK_TABLES_NUMBER_OF_DISPLAYED_ROWS,
    )


def _create_no_importance_task_table(master: tk.Misc) -> TaskTableWithName:
    return TaskTableWithName(
        master=master,
        id_column_width_pixels=2 * _IMPORTANCE_TASK_TABLES_ID_COLUMN_WIDTH_PIXELS,
        name_column_width_pixels=2 * _IMPORTANCE_TASK_TABLES_NAME_COLUMN_WIDTH_PIXELS,
        number_of_rows_displayed=2 * _IMPORTANCE_TASK_TABLES_NUMBER_OF_DISPLAYED_ROWS,
    )


class ImportanceBoard(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master)
        self._logic_layer = logic_layer

        self._show_completed_tasks = tk.BooleanVar()
        self._show_completed_tasks_checkbutton = ttk.Checkbutton(
            self,
            text="Show completed tasks",
            variable=self._show_completed_tasks,
            command=self._on_show_completed_tasks_button_toggled,
        )
        self._show_completed_tasks.set(False)

        self._inferred_header = tk.Label(self, text="Inferred")
        self._explicit_header = tk.Label(self, text="Explicit")

        self._high_importance_header = tk.Label(
            self,
            text="High",
            background=str(domain_visual_language.HIGH_IMPORTANCE_COLOUR),
        )
        self._high_importance_inferred_tasks = _create_importance_task_table(self)
        self._high_importance_explicit_tasks = _create_importance_task_table(self)

        self._medium_importance_header = tk.Label(
            self,
            text="Medium",
            background=str(domain_visual_language.MEDIUM_IMPORTANCE_COLOUR),
        )
        self._medium_importance_inferred_tasks = _create_importance_task_table(self)
        self._medium_importance_explicit_tasks = _create_importance_task_table(self)

        self._low_importance_header = tk.Label(
            self,
            text="Low",
            background=str(domain_visual_language.LOW_IMPORTANCE_COLOUR),
        )
        self._low_importance_inferred_tasks = _create_importance_task_table(self)
        self._low_importance_explicit_tasks = _create_importance_task_table(self)

        self._no_importance_header = tk.Label(self, text="None", background=str(GREY))
        self._no_importance_tasks = _create_no_importance_task_table(self)

        self._show_completed_tasks_checkbutton.grid(row=0, column=0, columnspan=3)

        self._inferred_header.grid(row=1, column=1)
        self._explicit_header.grid(row=1, column=2)

        self._high_importance_header.grid(row=2, column=0)
        self._high_importance_inferred_tasks.grid(row=2, column=1)
        self._high_importance_explicit_tasks.grid(row=2, column=2)

        self._medium_importance_header.grid(row=3, column=0)
        self._medium_importance_inferred_tasks.grid(row=3, column=1)
        self._medium_importance_explicit_tasks.grid(row=3, column=2)

        self._low_importance_header.grid(row=4, column=0)
        self._low_importance_inferred_tasks.grid(row=4, column=1)
        self._low_importance_explicit_tasks.grid(row=4, column=2)

        self._no_importance_header.grid(row=5, column=0)
        self._no_importance_tasks.grid(row=5, column=1, columnspan=2)

        broker = event_broker.get_singleton()
        broker.subscribe(event_broker.SystemModified, lambda _: self._update_tasks())

        self._update_tasks()

    def _get_importance_type(self, task: tasks.UID) -> ImportanceType:
        return (
            ImportanceType.INFERRED
            if self._logic_layer.get_task_system().has_inferred_importance(task)
            else ImportanceType.EXPLICIT
        )

    def _update_tasks(self) -> None:
        @dataclasses.dataclass
        class TasksAndTable:
            tasks: list[tasks.UID]
            table: TaskTableWithName

        importance_type_tasks_map = {
            Importance.HIGH: {
                ImportanceType.INFERRED: TasksAndTable(
                    list[tasks.UID](), self._high_importance_inferred_tasks
                ),
                ImportanceType.EXPLICIT: TasksAndTable(
                    list[tasks.UID](), self._high_importance_explicit_tasks
                ),
            },
            Importance.MEDIUM: {
                ImportanceType.INFERRED: TasksAndTable(
                    list[tasks.UID](), self._medium_importance_inferred_tasks
                ),
                ImportanceType.EXPLICIT: TasksAndTable(
                    list[tasks.UID](), self._medium_importance_explicit_tasks
                ),
            },
            Importance.LOW: {
                ImportanceType.INFERRED: TasksAndTable(
                    list[tasks.UID](), self._low_importance_inferred_tasks
                ),
                ImportanceType.EXPLICIT: TasksAndTable(
                    list[tasks.UID](), self._low_importance_explicit_tasks
                ),
            },
        }
        tasks_no_importance = list[tasks.UID]()

        tasks_matching_current_filter = self._get_tasks_matching_current_filter()
        for task, importance in zip(
            tasks_matching_current_filter,
            self._logic_layer.get_task_system().get_importances(
                tasks_matching_current_filter
            ),
            strict=True,
        ):
            match importance:
                case Importance.HIGH | Importance.MEDIUM | Importance.LOW:
                    importance_type_tasks_map[importance][
                        self._get_importance_type(task)
                    ].tasks.append(task)
                case None:
                    tasks_no_importance.append(task)

        importance_status_tasks_and_tables = (
            task1
            for status_tasks_map in importance_type_tasks_map.values()
            for task1 in status_tasks_map.values()
        )

        for container in itertools.chain(
            importance_status_tasks_and_tables,
            [TasksAndTable(tasks_no_importance, self._no_importance_tasks)],
        ):
            tasks_with_names = (
                (
                    task,
                    self._logic_layer.get_task_system()
                    .attributes_register()[task]
                    .name,
                )
                for task in container.tasks
            )
            container.table.update_tasks(tasks_with_names)

    def _get_tasks_matching_current_filter(self) -> tasks.TasksView:
        return (
            self._logic_layer.get_task_system().tasks()
            if self._show_completed_tasks.get()
            else tasks.get_incomplete_system(
                self._logic_layer.get_task_system()
            ).tasks()
        )

    def _on_show_completed_tasks_button_toggled(self) -> None:
        self._update_tasks()
