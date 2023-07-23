
import typer

from graft import architecture
from graft.typer_cli.logic_layer import assert_logic_layer_initialised

app = typer.Typer()
_logic_layer: architecture.LogicLayer = None


@app.command()
@assert_logic_layer_initialised
def create() -> None:
    """Create a new task."""
    typer.echo("Creating new task")
