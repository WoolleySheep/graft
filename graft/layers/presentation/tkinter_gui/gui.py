import logging
import tkinter as tk
from types import TracebackType

from graft import app_name, architecture, version
from graft.layers.presentation.tkinter_gui.tabs.tabs import Tabs
from graft.layers.presentation.tkinter_gui.tabs.task_panel.creation_deletion_panel.task_creation_window import (
    TaskCreationWindow,
)
from graft.layers.presentation.tkinter_gui.task_details import TaskDetails
from graft.layers.presentation.tkinter_gui.unknown_exception_failed_operation_window import (
    UnknownExceptionOperationFailedWindow,
)

logger = logging.getLogger(__name__)


class GUI(tk.Tk):
    def __init__(self, logic_layer: architecture.LogicLayer) -> None:
        super().__init__()
        self._logic_layer = logic_layer
        self.title(
            f"{app_name.APP_NAME} v{version.MAJOR_VERSION}.{version.MINOR_VERSION}.{version.PATCH_VERSION}"
        )
        self.report_callback_exception = self._log_exception_and_show_error_window

        self._create_new_task_button = tk.Button(
            master=self, text="New Task", command=self._open_new_task_window
        )
        self._tabs = Tabs(self, logic_layer)
        self._task_details = TaskDetails(self, logic_layer)

        self._create_new_task_button.grid(row=0, column=0)
        self._tabs.grid(row=1, column=0)
        self._task_details.grid(row=0, column=1, rowspan=2)

    def run(self) -> None:
        self.mainloop()

    def _log_exception_and_show_error_window(
        self,
        exception_type: type[BaseException],
        exception: BaseException,
        traceback: TracebackType | None,
    ) -> None:
        logger.error(
            "Exception bubbled all the way to the top of the GUI",
            exc_info=(exception_type, exception, traceback),
        )
        # I don't feel like making this class take base exception, so I'm just
        # going to live with the type mismatch and suppress the error
        UnknownExceptionOperationFailedWindow(master=self, exception=exception)

    def _open_new_task_window(self) -> None:
        TaskCreationWindow(master=self, logic_layer=self._logic_layer)


def run(logic_layer: architecture.LogicLayer) -> None:
    gui = GUI(logic_layer)
    gui.run()
