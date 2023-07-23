import typer

from graft import architecture
from graft.typer_cli import task
from graft.typer_cli.logic_layer import assert_logic_layer_initialised

_app = typer.Typer()
_app.add_typer(typer_instance=task.app, name="task", help="Task management")


class TyperCLIPresentationLayer(architecture.PresentationLayer):
    """Typer CLI presentation layer."""

    def __init__(self, logic_layer_: architecture.LogicLayer) -> None:
        """Initialise Typer CLI presentation layer.

        Set the logic layer shared by the typer cli module.
        """
        global logic_layer
        logic_layer = logic_layer_
        super().__init__(logic_layer=logic_layer_)

    def run(self) -> None:
        """Run the typer CLI."""
        _app()


@_app.command()
@assert_logic_layer_initialised
def init() -> None:
    """Initialise graft."""
    typer.echo("Initialising graft")
