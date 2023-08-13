import typer

from graft.typer_cli.logic_layer import check_logic_layer_initialised

app = typer.Typer()


@app.command()
@check_logic_layer_initialised
def create() -> None:
    """Create a new task."""
    typer.echo("Creating new task")
