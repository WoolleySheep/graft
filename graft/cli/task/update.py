import typer

from graft.io import load_task_register, save_task_register
from graft.objects.task import Description, Id, Importance, Name, Progress

app = typer.Typer()


@app.command()
def name(id: str, name: str) -> None:
    typer.echo(f"Updating task [{id}] name to [{name}]")
    id = Id(id)
    name = Name(name)
    task_register = load_task_register()

    task = task_register[id]

    task.name = name

    save_task_register(task_register)


@app.command()
def description(id: str, description: str) -> None:
    typer.echo(f"Updating task [{id}] description to [{description}]")
    id = Id(id)
    description = Description(description)
    task_register = load_task_register()

    task = task_register[id]

    task.description = description

    save_task_register(task_register)


@app.command()
def importance(id: str, importance: Importance) -> None:
    typer.echo(f"Updating task [{id}] importance to [{importance.value}]")
    id = Id(id)

    task_register = load_task_register()

    task = task_register[id]

    task.importance = importance

    save_task_register(task_register)


@app.command()
def progress(id: str, progress: Progress) -> None:
    typer.echo(f"Updating task [{id}] progress to [{progress.value}]")
    id = Id(id)

    task_register = load_task_register()

    task = task_register[id]

    task.progress = progress

    save_task_register(task_register)
