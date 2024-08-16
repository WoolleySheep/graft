import dataclasses
import enum
import tkinter as tk

from graft import architecture
from graft.domain import tasks
from graft.domain.tasks.importance import Importance
from graft.tkinter_gui import event_broker
from graft.tkinter_gui.helpers import TaskTable


class ImportanceType(enum.Enum):
    INFERRED = "inferred"
    EXPLICIT = "explicit"


class ImportanceBoard(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master)
        self._logic_layer = logic_layer

        self._inferred_header = tk.Label(self, text="Inferred")
        self._explicit_header = tk.Label(self, text="Explicit")

        self._high_importance_header = tk.Label(self, text="High")
        self._high_importance_inferred_tasks = TaskTable(self)
        self._high_importance_explicit_tasks = TaskTable(self)

        self._medium_importance_header = tk.Label(self, text="Medium")
        self._medium_importance_inferred_tasks = TaskTable(self)
        self._medium_importance_explicit_tasks = TaskTable(self)

        self._low_importance_header = tk.Label(self, text="Low")
        self._low_importance_inferred_tasks = TaskTable(self)
        self._low_importance_explicit_tasks = TaskTable(self)

        self._no_importance_header = tk.Label(self, text="None")
        self._no_importance_tasks = TaskTable(self)

        self._inferred_header.grid(row=0, column=1)
        self._explicit_header.grid(row=0, column=2)

        self._high_importance_header.grid(row=1, column=0)
        self._high_importance_inferred_tasks.grid(row=1, column=1)
        self._high_importance_explicit_tasks.grid(row=1, column=2)

        self._medium_importance_header.grid(row=2, column=0)
        self._medium_importance_inferred_tasks.grid(row=2, column=1)
        self._medium_importance_explicit_tasks.grid(row=2, column=2)

        self._low_importance_header.grid(row=3, column=0)
        self._low_importance_inferred_tasks.grid(row=3, column=1)
        self._low_importance_explicit_tasks.grid(row=3, column=2)

        self._no_importance_header.grid(row=4, column=0)
        self._no_importance_tasks.grid(row=4, column=1, columnspan=2)

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
            table: TaskTable

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

        for task in self._logic_layer.get_task_system():
            match importance := self._logic_layer.get_task_system().get_importance(
                task
            ):
                case Importance.HIGH | Importance.MEDIUM | Importance.LOW:
                    importance_type_tasks_map[importance][
                        self._get_importance_type(task)
                    ].tasks.append(task)
                case None:
                    tasks_no_importance.append(task)

        for status_tasks_map in importance_type_tasks_map.values():
            for container in status_tasks_map.values():
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

        tasks_no_importance_with_names = (
            (task, self._logic_layer.get_task_system().attributes_register()[task].name)
            for task in tasks_no_importance
        )
        self._no_importance_tasks.update_tasks(tasks_no_importance_with_names)
