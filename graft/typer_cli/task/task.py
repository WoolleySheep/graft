"""Task-related commands."""

import typer

from graft.typer_cli import global_logic_layer

app = typer.Typer()


@app.command()
@global_logic_layer.check_initialised
def create() -> None:
    """Create a new task."""
    typer.echo("Creating new task")
    logic_layer = global_logic_layer.get_logic_layer()
    try:
        uid = logic_layer.create_task()
    except Exception as e:
        typer.echo(f"Failed to create task: {e}")
        raise
    typer.echo(f"Task [{uid}] created")
