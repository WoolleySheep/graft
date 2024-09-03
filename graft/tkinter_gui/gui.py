import logging
import tkinter as tk
from types import TracebackType

from graft import app_name, architecture
from graft.tkinter_gui.helpers import UnknownExceptionOperationFailedWindow
from graft.tkinter_gui.tabs.tabs import Tabs
from graft.tkinter_gui.task_details import TaskDetails

logger = logging.getLogger(__name__)


class GUI(tk.Tk):
    def __init__(self, logic_layer: architecture.LogicLayer) -> None:
        super().__init__()
        self._logic_layer = logic_layer
        self.title(app_name.APP_NAME)
        self.report_callback_exception = self._log_exception_and_show_error_window

        self._tabs = Tabs(self, logic_layer)
        self._task_details = TaskDetails(self, logic_layer)

        self._tabs.grid(row=0, column=0)
        self._task_details.grid(row=0, column=1)

    def run(self) -> None:
        self.mainloop()

    def _log_exception_and_show_error_window(
        self,
        exception_type: type[BaseException],
        exception: BaseException,
        traceback: TracebackType | None,
    ):
        logger.error(
            "Exception bubbled all the way to the top of the GUI",
            exc_info=(exception_type, exception, traceback),
        )
        # I don't feel like making this class take base exception, so I'm just
        # going to live with the type mismatch and suppress the error
        UnknownExceptionOperationFailedWindow(master=self, exception=exception)  # type: ignore[reportArgumentType]


def run(logic_layer: architecture.LogicLayer) -> None:
    gui = GUI(logic_layer)
    gui.run()
