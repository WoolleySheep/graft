import typer

from graft.io import load_task_dependencies, save_task_dependencies
from graft.objects.task import Id

app = typer.Typer()


@app.command()
def create(blocking_id: str, blocked_id) -> None:
    typer.echo(f"Creating dependency - task [{blocking_id}] blocks task [{blocked_id}]")
    blocking_id = Id(blocking_id)
    blocked_id = Id(blocked_id)

    task_dependencies = load_task_dependencies()

    task_dependencies.add_edge(blocking_id, blocked_id)

    save_task_dependencies(task_dependencies)


@app.command()
def delete(blocking_id: str, blocked_id) -> None:
    typer.echo(
        f"Deleting dependency - task [{blocking_id}] does not block task [{blocked_id}]"
    )
    blocking_id = Id(blocking_id)
    blocked_id = Id(blocked_id)

    task_dependencies = load_task_dependencies()

    task_dependencies.remove_edge(blocking_id, blocked_id)

    save_task_dependencies(task_dependencies)
