"""Task-related commands."""

import typer

from graft.domain import tasks
from graft.typer_cli import global_logic_layer
from graft.typer_cli.task.dependency import app as dependency_app
from graft.typer_cli.task.hierarchy import app as hierarchy_app

app = typer.Typer()
app.add_typer(
    typer_instance=hierarchy_app, name="hierarchy", help="Hierarchy commands."
)
app.add_typer(
    typer_instance=dependency_app, name="dependency", help="Dependency commands."
)


@app.command()
def create() -> None:
    """Create a new task."""
    typer.echo("Creating new task")
    try:
        logic_layer = global_logic_layer.get_logic_layer()
        uid = logic_layer.create_task()
    except Exception as e:
        typer.echo(f"Failed to create task; exception [{e}] raised")
        raise
    typer.echo(f"Task [{uid}] created")


@app.command()
def delete(task: int) -> None:
    """Delete a task."""
    typer.echo(f"Deleting task [{task}]")

    try:
        task_uid = tasks.UID(task)
    except tasks.InvalidUIDNumberError:
        typer.echo(f"Failed to delete task; [{task}] is an invalid UID")
        raise

    try:
        logic_layer = global_logic_layer.get_logic_layer()
        logic_layer.delete_task(task_uid)
    except Exception as e:
        typer.echo(f"Failed to delete task; exception [{e}] raised")
        raise

    typer.echo(f"Task [{task_uid}] deleted")


@app.command()
def ls() -> None:
    """List all tasks."""
    typer.echo("Listing tasks")
    try:
        logic_layer = global_logic_layer.get_logic_layer()
        register = logic_layer.get_task_attributes_register_view()
    except Exception as e:
        typer.echo(f"Failed to list tasks; exception [{e}] raised")
        raise

    for uid, attributes in sorted(register.items()):
        typer.echo(f"[{uid}] {attributes.name or ""} : {attributes.description or ""}")
