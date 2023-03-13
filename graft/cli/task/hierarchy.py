import typer

from graft.io import load_task_hierarchies, save_task_hierarchies
from graft.objects.task import Id

app = typer.Typer()


@app.command()
def create(parent_id: str, child_id: str) -> None:
    typer.echo(
        f"Creating hierarchy - task [{parent_id}] is the parent of task [{child_id}]"
    )

    parent_id = Id(parent_id)
    child_id = Id(child_id)

    task_hierarchies = load_task_hierarchies()

    task_hierarchies.add_edge(parent_id, child_id)

    save_task_hierarchies(task_hierarchies)


@app.command()
def delete(parent_id: str, child_id: str) -> None:
    typer.echo(
        f"Deleting hierarchy - task [{parent_id}] is not the parent of task [{child_id}]"
    )
    parent_id = Id(parent_id)
    child_id = Id(child_id)

    task_hierarchies = load_task_hierarchies()

    task_hierarchies.remove_edge(parent_id, child_id)

    save_task_hierarchies(task_hierarchies)
