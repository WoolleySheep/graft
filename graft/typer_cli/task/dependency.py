"""Dependency-related commands."""


import typer

from graft.domain import tasks
from graft.typer_cli import global_logic_layer

app = typer.Typer()


@app.command()
def create(dependee_task: int, dependent_task: int) -> None:
    """Create a new dependency between the specified tasks."""
    typer.echo(
        f"Creating dependency between dependent-task [{dependent_task}] and dependee-task [{dependee_task}]"
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
            dependee_task=dependee_task_uid, dependent_task=dependee_task_uid
        )
    except Exception as e:
        typer.echo(f"Failed to create dependency; exception [{e}] raised")
        raise

    typer.echo(
        f"Dependency created between dependent-task [{dependent_task}] and dependee-task [{dependee_task}]"
    )
