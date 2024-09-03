"""Functions for starting the graft application."""

import logging

from graft import tkinter_gui
from graft.layers import data, logic

logger = logging.getLogger(__name__)


def run() -> None:
    """Run the application."""
    logger.info("Starting graft application")
    data_layer = data.LoggingDecoratorDataLayer(
        handler=data.CachingDecoratorDataLayer(handler=data.LocalFilesDataLayer())
    )
    logic_layer = logic.LoggingDecoratorLogicLayer(
        handler=logic.StandardLogicLayer(data_layer=data_layer)
    )
    tkinter_gui.run(logic_layer=logic_layer)
    logger.info("Shutting down graft application")
