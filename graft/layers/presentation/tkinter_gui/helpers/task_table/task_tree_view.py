import dataclasses
import tkinter as tk
from collections.abc import Callable, Iterable
from tkinter import ttk
from typing import TypeVarTuple

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import event_broker

Ts = TypeVarTuple("Ts")


def sort_by_task_id[*Ts](
    tasks_with_info: Iterable[tuple[tasks.UID, *Ts]],
) -> list[tuple[tasks.UID, *Ts]]:
    return sorted(tasks_with_info, key=lambda task_with_info: task_with_info[0])


@dataclasses.dataclass
class ColumnParameters:
    header: str
    width_pixels: int | None


@dataclasses.dataclass
class ColumnDetails:
    """Only meant to be used within this file."""

    id: int | str
    parameters: ColumnParameters


class TaskTreeView[*Ts](ttk.Treeview):
    """Tree view with task ID as the first column.

    Ensure the number of values passed in matches the number of columns .
    """

    def __init__(
        self,
        master: tk.Misc,
        column_parameters: Iterable[ColumnParameters],
        sort_rows: Callable[
            [Iterable[tuple[tasks.UID, tuple[*Ts]]]],
            Iterable[tuple[tasks.UID, tuple[*Ts]]],
        ] = sort_by_task_id,
        id_column_width_pixels: int | None = None,
        number_of_rows_displayed: int = 10,
        id_column_index: int = 0,
    ) -> None:
        if id_column_index < 0:
            msg = "id_column_index must be non-negative"
            raise ValueError(msg)

        column_details: list[ColumnDetails] = [
            ColumnDetails(id, parameters)
            for id, parameters in enumerate(column_parameters)
        ]

        if id_column_index > len(column_details):
            msg = "id_column_index must be less than or equal to the number of columns"
            raise ValueError(msg)

        column_details.insert(
            id_column_index,
            ColumnDetails("id", ColumnParameters("ID", id_column_width_pixels)),
        )

        column_ids = [details.id for details in column_details]
        super().__init__(
            master, columns=column_ids, show="headings", height=number_of_rows_displayed
        )
        self._id_column_index = id_column_index
        self._sort_rows = sort_rows

        for details in column_details:
            self.heading(details.id, text=details.parameters.header)
            if details.parameters.width_pixels is not None:
                self.column(details.id, width=details.parameters.width_pixels)

        self.bind("<<TreeviewSelect>>", lambda _: self._publish_task_selected_event())

    def _publish_task_selected_event(self) -> None:
        item_id = self.focus()

        # TODO: Fix this hack. When deleting all the items in the tree (as is
        # done in update_tasks), a TreeviewSelect event is generated. To stop
        # this running again (when no item is selected, this method fails) added
        # this guard clause here.
        if not item_id:
            return

        item_values = self.item(item_id, "values")
        formatted_task = item_values[self._id_column_index]
        task = tasks.UID(int(formatted_task))

        broker = event_broker.get_singleton()
        broker.publish(event_broker.TaskSelected(task))

    def update_tasks(self, task_rows: Iterable[tuple[tasks.UID, tuple[*Ts]]]) -> None:
        """Update the tasks displayed."""
        self.delete(*self.get_children())

        for task, information in self._sort_rows(task_rows):
            row = [str(value) for value in information]
            row.insert(self._id_column_index, str(task))
            self.insert(
                "",
                tk.END,
                values=row,
            )
