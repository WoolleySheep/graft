import functools
import tkinter as tk
from collections.abc import Callable, Generator, Iterable
from tkinter import ttk
from typing import TypeVarTuple

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.helpers.task_table.task_tree_view import (
    ColumnParameters,
    TaskTreeView,
    sort_by_task_id,
)

Ts = TypeVarTuple("Ts")


def adapt_sort_rows[*Ts](
    fn: Callable[[Iterable[tuple[tasks.UID, *Ts]]], Iterable[tuple[tasks.UID, *Ts]]],
) -> Callable[
    [Iterable[tuple[tasks.UID, tuple[*Ts]]]],
    Generator[tuple[tasks.UID, tuple[*Ts]], None, None],
]:
    """Make a flatted sort_rows function work in AdjustableTaskTable."""

    @functools.wraps(fn)
    def inner(
        row: Iterable[tuple[tasks.UID, tuple[*Ts]]],
    ) -> Generator[tuple[tasks.UID, tuple[*Ts]]]:
        transformed_input = ((task, *info) for (task, info) in row)
        return (
            (task_with_info[0], task_with_info[1:])
            for task_with_info in fn(transformed_input)
        )

    return inner


class AdjustableTaskTable[*Ts](tk.Frame):
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
        super().__init__(master)
        self._task_tree_view = TaskTreeView(
            self,
            column_parameters=column_parameters,
            sort_rows=sort_rows,
            id_column_width_pixels=id_column_width_pixels,
            number_of_rows_displayed=number_of_rows_displayed,
            id_column_index=id_column_index,
        )

        self._scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self._task_tree_view.yview
        )

        self._task_tree_view.configure(yscrollcommand=self._scrollbar.set)

        self._task_tree_view.grid(row=0, column=0)
        # Place the scrollbar on the right side of the Treeview
        self._scrollbar.grid(row=0, column=1, sticky="ns")

    def update_tasks(self, task_rows: Iterable[tuple[tasks.UID, tuple[*Ts]]]) -> None:
        """Update the tasks displayed."""
        self._task_tree_view.update_tasks(task_rows)
