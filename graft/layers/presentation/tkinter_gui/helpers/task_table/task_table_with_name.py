import tkinter as tk
from collections.abc import Callable, Iterable

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.helpers.task_table.adjustable_task_table import (
    AdjustableTaskTable,
    ColumnParameters,
    adapt_sort_rows,
)
from graft.layers.presentation.tkinter_gui.helpers.task_table.task_tree_view import (
    sort_by_task_id,
)

_ID_COLUMN_INDEX = 0


class TaskTableWithName(tk.Frame):
    """Task table with name column."""

    def __init__(
        self,
        master: tk.Misc,
        id_column_width_pixels: int | None = None,
        name_column_width_pixels: int | None = None,
        sort_rows: Callable[
            [Iterable[tuple[tasks.UID, tasks.Name]]],
            Iterable[tuple[tasks.UID, tasks.Name]],
        ] = sort_by_task_id,
        number_of_rows_displayed: int = 10,
    ) -> None:
        super().__init__(master)

        self._adjustable_task_table = AdjustableTaskTable[tasks.Name](
            self,
            column_parameters=[ColumnParameters("Name", name_column_width_pixels)],
            sort_rows=adapt_sort_rows(sort_rows),
            id_column_width_pixels=id_column_width_pixels,
            number_of_rows_displayed=number_of_rows_displayed,
            id_column_index=_ID_COLUMN_INDEX,
        )

        self._adjustable_task_table.grid()

    def update_tasks(
        self, tasks_with_names: Iterable[tuple[tasks.UID, tasks.Name]]
    ) -> None:
        self._adjustable_task_table.update_tasks(
            (task, (name,)) for (task, name) in tasks_with_names
        )
