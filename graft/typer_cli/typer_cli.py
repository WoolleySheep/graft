"""Typer CLI presentation-layer implementation and associated exceptions."""

import typer

from graft import architecture
from graft.typer_cli import global_logic_layer, task

_app = typer.Typer()
_app.add_typer(typer_instance=task.app, name="task", help="Task management")


class TyperCLIPresentationLayer(architecture.PresentationLayer):
    """Typer CLI presentation layer."""

    def __init__(self, logic_layer: architecture.LogicLayer) -> None:
        """Initialise Typer CLI presentation layer.

        Set the logic layer shared by the typer cli module.
        """
        global_logic_layer.set(logic_layer=logic_layer)
        super().__init__(logic_layer=logic_layer)

    def run(self) -> None:
        """Run the typer CLI."""
        _app()


@_app.command()
@global_logic_layer.check_initialised
def init() -> None:
    """Initialise graft."""
    typer.echo("Initialising graft")
    logic_layer = global_logic_layer.get()
    try:
        logic_layer.initialise()
    except Exception as e:
        typer.echo(f"Failed to initialise graft: {e}")
        raise
