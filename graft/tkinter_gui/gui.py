import logging
import tkinter as tk
from types import TracebackType

from graft import app_name, architecture
from graft.tkinter_gui.tabs.tabs import Tabs
from graft.tkinter_gui.task_details import TaskDetails

logger = logging.getLogger(__name__)


def _log_exceptions(
    exception: type[BaseException],
    value: BaseException,
    traceback: TracebackType | None,
):
    logger.error(
        "Exception bubbled all the way to the top of the GUI",
        exc_info=(exception, value, traceback),
    )


class GUI(tk.Tk):
    def __init__(self, logic_layer: architecture.LogicLayer) -> None:
        super().__init__()
        self._logic_layer = logic_layer
        self.title(app_name.APP_NAME)
        self.report_callback_exception = _log_exceptions

        self._tabs = Tabs(self, logic_layer)
        self._task_details = TaskDetails(self, logic_layer)

        self._tabs.grid(row=0, column=0)
        self._task_details.grid(row=0, column=1)

    def run(self) -> None:
        # TODO: Set it up so any exceptions thrown by tkinter are logged
        self.mainloop()


def run(logic_layer: architecture.LogicLayer) -> None:
    gui = GUI(logic_layer)
    gui.run()
