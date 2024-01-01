"""Dependency-related commands."""


import typer

from graft.domain import tasks
from graft.typer_cli import global_logic_layer

app = typer.Typer()


@app.command()
def ls() -> None:
    """List all dependencies."""
    typer.echo("Listing all dependencies")
    try:
        logic_layer = global_logic_layer.get_logic_layer()
        graph = logic_layer.get_dependency_graph_view()
    except Exception as e:
        typer.echo(f"Failed to list dependencies; exception [{e}] raised")
        raise

    for dependee_task, dependent_task in sorted(graph.dependencies()):
        typer.echo(f"[{dependee_task}] -> [{dependent_task}]")


@app.command()
def create(dependee_task: int, dependent_task: int) -> None:
    """Create a new dependency between the specified tasks."""
    typer.echo(
        f"Creating dependency between dependee-task [{dependee_task}] and dependent-task [{dependent_task}]"
    )

    try:
        dependee_task_uid = tasks.UID(dependee_task)
    except tasks.InvalidUIDNumberError:
        typer.echo(
            f"Failed to create dependency; dependee-task [{dependee_task}] is an invalid UID"
        )
        raise

    try:
        dependent_task_uid = tasks.UID(dependent_task)
    except tasks.InvalidUIDNumberError:
        typer.echo(
            f"Failed to create dependency; dependent-task [{dependent_task}] is an invalid UID"
        )
        raise

    try:
        logic_layer = global_logic_layer.get_logic_layer()
        logic_layer.create_dependency(
            dependee_task=dependee_task_uid, dependent_task=dependent_task_uid
        )
    except Exception as e:
        typer.echo(f"Failed to create dependency; exception [{e}] raised")
        raise

    typer.echo(
        f"Created dependency between dependee-task [{dependee_task}] and dependent-task [{dependent_task}]"
    )


@app.command()
def delete(dependee_task: int, dependent_task: int) -> None:
    """Delete a dependency between the specified tasks."""
    typer.echo(
        f"Deleting dependency between dependee-task [{dependee_task}] and dependent-task [{dependent_task}]"
    )

    try:
        dependee_task_uid = tasks.UID(dependee_task)
    except tasks.InvalidUIDNumberError:
        typer.echo(
            f"Failed to delete dependency; dependee-task [{dependee_task}] is an invalid UID"
        )
        raise

    try:
        dependent_task_uid = tasks.UID(dependent_task)
    except tasks.InvalidUIDNumberError:
        typer.echo(
            f"Failed to delete dependency; dependent-task [{dependent_task}] is an invalid UID"
        )
        raise

    try:
        logic_layer = global_logic_layer.get_logic_layer()
        logic_layer.delete_dependency(
            dependee_task=dependee_task_uid, dependent_task=dependent_task_uid
        )
    except Exception as e:
        typer.echo(f"Failed to delete dependency; exception [{e}] raised")
        raise

    typer.echo(
        f"Deleted dependency between dependee-task [{dependee_task}] and dependent-task [{dependent_task}]"
    )
