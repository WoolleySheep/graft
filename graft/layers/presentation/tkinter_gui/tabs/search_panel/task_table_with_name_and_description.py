import functools
import tkinter as tk
from collections.abc import Callable, Generator, Iterable

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import helpers

_ID_COLUMN_INDEX = 0


def adapt_sort_rows(
    fn: Callable[
        [Iterable[tuple[tasks.UID, tasks.Name, tasks.Description]]],
        Iterable[tuple[tasks.UID, tasks.Name, tasks.Description]],
    ],
) -> Callable[
    [Iterable[tuple[tasks.UID, tuple[tasks.Name, tasks.Description]]]],
    Generator[tuple[tasks.UID, tuple[tasks.Name, tasks.Description]], None, None],
]:
    """Make the sort_rows function passed into this function work in AdjustableTaskTable."""

    @functools.wraps(fn)
    def inner(
        row: Iterable[tuple[tasks.UID, tuple[tasks.Name, tasks.Description]]],
    ) -> Generator[tuple[tasks.UID, tuple[tasks.Name, tasks.Description]]]:
        transformed_input = ((task, info[0], info[1]) for (task, info) in row)
        return (
            (task, (name, description))
            for (task, name, description) in fn(transformed_input)
        )

    return inner


class TaskTableWithNameAndDescription(tk.Frame):
    """Task table with name and description columns."""

    def __init__(
        self,
        master: tk.Misc,
        id_column_width_pixels: int | None = None,
        name_column_width_pixels: int | None = None,
        description_column_width_pixels: int | None = None,
        sort_rows: Callable[
            [Iterable[tuple[tasks.UID, tasks.Name, tasks.Description]]],
            Iterable[tuple[tasks.UID, tasks.Name, tasks.Description]],
        ] = helpers.sort_rows_by_task_id,
        number_of_rows_displayed: int = 10,
    ) -> None:
        super().__init__(master)

        self._adjustable_task_table = helpers.AdjustableTaskTable[
            tasks.Name, tasks.Description
        ](
            self,
            column_parameters=[
                helpers.TaskTableColumnParameters("Name", name_column_width_pixels),
                helpers.TaskTableColumnParameters(
                    "Description", description_column_width_pixels
                ),
            ],
            sort_rows=adapt_sort_rows(sort_rows),
            id_column_width_pixels=id_column_width_pixels,
            number_of_rows_displayed=number_of_rows_displayed,
            id_column_index=_ID_COLUMN_INDEX,
        )

        self._adjustable_task_table.grid()

    def update_tasks(
        self, tasks_info: Iterable[tuple[tasks.UID, tasks.Name, tasks.Description]]
    ) -> None:
        self._adjustable_task_table.update_tasks(
            (task, (name, description)) for (task, name, description) in tasks_info
        )
