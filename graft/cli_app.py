"""Functions for starting the graft application."""

from graft import local_file, standard, typer_cli


def run() -> None:
    """Run the application."""
    data_layer = local_file.LocalFileDataLayer()
    logic_layer = standard.StandardLogicLayer(data_layer=data_layer)
    typer_cli.run_app(logic_layer=logic_layer)
