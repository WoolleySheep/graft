"""Hierarchy-related commands."""


import typer

from graft.domain import tasks
from graft.typer_cli import global_logic_layer

app = typer.Typer()

@app.command()
def ls() -> None:
    """List all hierarchies."""
    typer.echo("Listing all hierarchies")
    try:
        logic_layer = global_logic_layer.get_logic_layer()
        graph = logic_layer.get_hierarchy_graph_view()
    except Exception as e:
        typer.echo(f"Failed to list hierarchies; exception [{e}] raised")
        raise

    for supertask, subtask in sorted(graph.hierarchies()):
        typer.echo(f"[{supertask}] -> [{subtask}]")



@app.command()
def create(supertask: int, subtask: int) -> None:
    """Create a new hierarchy between the specified tasks."""
    typer.echo(
        f"Creating hierarchy between supertask [{supertask}] and subtask [{subtask}]"
    )

    try:
        supertask_uid = tasks.UID(supertask)
    except tasks.InvalidUIDNumberError:
        typer.echo(
            f"Failed to create hierarchy; supertask [{supertask}] is an invalid UID"
        )
        raise

    try:
        subtask_uid = tasks.UID(subtask)
    except tasks.InvalidUIDNumberError:
        typer.echo(f"Failed to create hierarchy; subtask [{subtask}] is an invalid UID")
        raise

    try:
        logic_layer = global_logic_layer.get_logic_layer()
        logic_layer.create_hierarchy(supertask=supertask_uid, subtask=subtask_uid)
    except Exception as e:
        typer.echo(f"Failed to create hierarchy; exception [{e}] raised")
        raise

    typer.echo(
        f"Hierarchy created between supertask [{supertask}] and subtask [{subtask}]"
    )


@app.command()
def delete(supertask: int, subtask: int) -> None:
    """Delete a hierarchy between the specified tasks."""
    typer.echo(
        f"Deleting hierarchy between supertask [{supertask}] and subtask [{subtask}]"
    )

    try:
        supertask_uid = tasks.UID(supertask)
    except tasks.InvalidUIDNumberError:
        typer.echo(
            f"Failed to delete hierarchy; supertask [{supertask}] is an invalid UID"
        )
        raise

    try:
        subtask_uid = tasks.UID(subtask)
    except tasks.InvalidUIDNumberError:
        typer.echo(f"Failed to delete hierarchy; subtask [{subtask}] is an invalid UID")
        raise

    try:
        logic_layer = global_logic_layer.get_logic_layer()
        logic_layer.delete_hierarchy(supertask=supertask_uid, subtask=subtask_uid)
    except Exception as e:
        typer.echo(f"Failed to delete hierarchy; exception [{e}] raised")
        raise

    typer.echo(f"Deleted hierarchy between [{supertask}] and subtask [{subtask}]")
