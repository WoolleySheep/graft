"""Functions for starting the graft application."""

from graft import local_file, standard, tkinter_gui


def run() -> None:
    """Run the application."""
    data_layer = local_file.LocalFileDataLayer()
    logic_layer = standard.StandardLogicLayer(data_layer=data_layer)
    tkinter_gui.run(logic_layer=logic_layer)
