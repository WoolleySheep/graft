"""Task-related commands."""

import typer

from graft.domain import tasks
from graft.typer_cli import global_logic_layer

app = typer.Typer()


@app.command()
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


@app.command()
def delete(task: int) -> None:
    """Delete a task."""
    typer.echo(f"Deleting task [{task}]")

    try:
        task_uid = tasks.UID(task)
    except tasks.InvalidUIDNumberError:
        typer.echo(f"Failed to delete task: [{task}] is an invalid UID")
        raise

    logic_layer = global_logic_layer.get_logic_layer()

    try:
        logic_layer.delete_task(task_uid)
    except Exception as e:
        typer.echo(f"Failed to delete task: {e}")
        raise

    typer.echo(f"Task [{task_uid}] deleted")
