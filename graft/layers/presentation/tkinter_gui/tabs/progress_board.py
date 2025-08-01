import dataclasses
import enum
import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.domain.tasks.progress import Progress
from graft.layers.presentation.tkinter_gui import domain_visual_language, event_broker
from graft.layers.presentation.tkinter_gui.helpers import TaskTableWithName
from graft.layers.presentation.tkinter_gui.helpers.colour import WHITE

_TASK_TABLES_ID_COLUMN_WIDTH_PIXELS = 30
_TASK_TABLES_NAME_COLUMN_WIDTH_PIXELS = 130
_TASK_TABLES_NUMBER_OF_DISPLAYED_ROWS = 10


def _create_task_table(master: tk.Misc) -> TaskTableWithName:
    return TaskTableWithName(
        master=master,
        id_column_width_pixels=_TASK_TABLES_ID_COLUMN_WIDTH_PIXELS,
        name_column_width_pixels=_TASK_TABLES_NAME_COLUMN_WIDTH_PIXELS,
        number_of_rows_displayed=_TASK_TABLES_NUMBER_OF_DISPLAYED_ROWS,
    )


class ProgressType(enum.Enum):
    INFERRED = enum.auto()
    EXPLICIT = enum.auto()


class ProgressBoard(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master)
        self._show_completed_tasks = tk.BooleanVar()
        self._show_completed_tasks_checkbutton = ttk.Checkbutton(
            self,
            text="Show completed tasks",
            variable=self._show_completed_tasks,
            command=self._on_show_completed_tasks_button_toggled,
        )
        self._show_completed_tasks.set(False)

        self._logic_layer = logic_layer

        self._explicit_header = tk.Label(self, text="Explicit")
        self._inferred_header = tk.Label(self, text="Inferred")

        self._not_started_header = tk.Label(
            self,
            text="Not Started",
            background=str(domain_visual_language.NOT_STARTED_TASK_COLOUR),
            foreground=str(WHITE),
        )
        self._not_started_inferred_tasks = _create_task_table(self)
        self._not_started_explicit_tasks = _create_task_table(self)

        self._in_progress_header = tk.Label(
            self,
            text="In Progress",
            background=str(domain_visual_language.IN_PROGRESS_TASK_COLOUR),
        )
        self._in_progress_inferred_tasks = _create_task_table(self)
        self._in_progress_explicit_tasks = _create_task_table(self)

        self._completed_header = tk.Label(
            self,
            text="Completed",
            background=str(domain_visual_language.COMPLETED_TASK_COLOUR),
            foreground=str(WHITE),
        )
        self._completed_inferred_tasks = _create_task_table(self)
        self._completed_explicit_tasks = _create_task_table(self)

        self._show_completed_tasks_checkbutton.grid(row=0, column=0, columnspan=4)

        self._inferred_header.grid(row=2, column=0)
        self._explicit_header.grid(row=3, column=0)

        self._not_started_header.grid(row=1, column=1)
        self._not_started_inferred_tasks.grid(row=2, column=1)
        self._not_started_explicit_tasks.grid(row=3, column=1)

        self._in_progress_header.grid(row=1, column=2)
        self._in_progress_inferred_tasks.grid(row=2, column=2)
        self._in_progress_explicit_tasks.grid(row=3, column=2)

        self._completed_header.grid(row=1, column=3)
        self._completed_inferred_tasks.grid(row=2, column=3)
        self._completed_explicit_tasks.grid(row=3, column=3)

        broker = event_broker.get_singleton()
        broker.subscribe(event_broker.SystemModified, lambda _: self._update_tasks())

        self._update_tasks()

    def _get_progress_type(self, task: tasks.UID) -> ProgressType:
        return (
            ProgressType.EXPLICIT
            if self._logic_layer.get_task_system()
            .network_graph()
            .hierarchy_graph()
            .is_concrete(task)
            else ProgressType.INFERRED
        )

    def _update_tasks(self) -> None:
        @dataclasses.dataclass
        class TasksAndTable:
            tasks: list[tasks.UID]
            table: TaskTableWithName

        progress_type_tasks_map = {
            Progress.NOT_STARTED: {
                ProgressType.INFERRED: TasksAndTable(
                    list[tasks.UID](), self._not_started_inferred_tasks
                ),
                ProgressType.EXPLICIT: TasksAndTable(
                    list[tasks.UID](), self._not_started_explicit_tasks
                ),
            },
            Progress.IN_PROGRESS: {
                ProgressType.INFERRED: TasksAndTable(
                    list[tasks.UID](), self._in_progress_inferred_tasks
                ),
                ProgressType.EXPLICIT: TasksAndTable(
                    list[tasks.UID](), self._in_progress_explicit_tasks
                ),
            },
            Progress.COMPLETED: {
                ProgressType.INFERRED: TasksAndTable(
                    list[tasks.UID](), self._completed_inferred_tasks
                ),
                ProgressType.EXPLICIT: TasksAndTable(
                    list[tasks.UID](), self._completed_explicit_tasks
                ),
            },
        }

        tasks_ = self._get_tasks_matching_current_filter()
        for task, progress in zip(
            tasks_,
            self._logic_layer.get_task_system().get_progresses(tasks_),
            strict=True,
        ):
            progress_type_tasks_map[progress][
                self._get_progress_type(task)
            ].tasks.append(task)

        for type_tasks_map in progress_type_tasks_map.values():
            for container in type_tasks_map.values():
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
