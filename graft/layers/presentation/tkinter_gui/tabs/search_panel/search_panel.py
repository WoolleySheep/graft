import tkinter as tk
from collections.abc import Generator
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import event_broker
from graft.layers.presentation.tkinter_gui.tabs.search_panel.task_table_with_name_and_description import (
    TaskTableWithNameAndDescription,
)

_RESULTS_TABLE_ID_COLUMN_WIDTH_PIXELS = 30
_RESULTS_TABLE_NAME_COLUMN_WIDTH_PIXELS = 300
_RESULTS_TABLE_DESCRIPTION_COLUMN_WIDTH_PIXELS = 300
_RESULTS_TABLE_NUMBER_OF_DISPLAYED_ROWS = 20


class SearchPanel(tk.Frame):
    """Panel for searching for text in tasks.

    Allows user to filter tasks by looking for a substring in task names and
    descriptions.
    """

    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master)
        self._logic_layer = logic_layer

        # Search box
        self._search_string_entry = ttk.Entry(self)

        self._search_button = ttk.Button(
            self, text="Search", command=self._update_table_with_search_results
        )

        self._clear_button = ttk.Button(self, text="Clear", command=self._clear_search)

        self._results_table = TaskTableWithNameAndDescription(
            master=self,
            id_column_width_pixels=_RESULTS_TABLE_ID_COLUMN_WIDTH_PIXELS,
            name_column_width_pixels=_RESULTS_TABLE_NAME_COLUMN_WIDTH_PIXELS,
            description_column_width_pixels=_RESULTS_TABLE_DESCRIPTION_COLUMN_WIDTH_PIXELS,
            number_of_rows_displayed=_RESULTS_TABLE_NUMBER_OF_DISPLAYED_ROWS,
        )

        self._search_string_entry.grid(row=0, column=0)
        self._search_button.grid(row=0, column=1)
        self._clear_button.grid(row=0, column=2)
        self._results_table.grid(row=2, column=0, columnspan=3)

        self._update_table_with_search_results()

        broker = event_broker.get_singleton()
        broker.subscribe(event_broker.SystemModified, self._on_system_modified)

    def _clear_search(self) -> None:
        self._search_string_entry.delete(0, tk.END)
        self._update_table_with_search_results()

    def _on_system_modified(self, event: event_broker.Event) -> None:
        if not isinstance(event, event_broker.SystemModified):
            raise ValueError

        self._update_table_with_search_results()

    def _get_search_string(self) -> str:
        return self._search_string_entry.get()

    def _get_tasks_that_match_search_criteria(self) -> Generator[tasks.UID, None, None]:
        search_string = self._get_search_string()

        for task, attributes in (
            self._logic_layer.get_task_system().attributes_register().items()
        ):
            if (
                search_string in str(attributes.name).lower()
                or search_string in str(attributes.description).lower()
            ):
                yield task

    def _update_table_with_search_results(self) -> None:
        register = self._logic_layer.get_task_system().attributes_register()
        tasks_with_info = (
            (task, register[task].name, register[task].description)
            for task in self._get_tasks_that_match_search_criteria()
        )
        self._results_table.update_tasks(tasks_with_info)
