import typer

from graft.cli.task.dependency import app as dependency_app
from graft.cli.task.hierarchy import app as hierarchy_app
from graft.cli.task.update import app as update_app
from graft.io import (
    get_next_task_id,
    increment_task_id_count,
    load_event_register,
    load_event_task_due_table,
    load_task_dependencies,
    load_task_hierarchies,
    load_task_register,
    save_task_dependencies,
    save_task_hierarchies,
    save_task_register,
)
from graft.objects.task import Id, Task

app = typer.Typer()

app.add_typer(typer_instance=update_app, name="update")
app.add_typer(typer_instance=hierarchy_app, name="hierarchy")
app.add_typer(typer_instance=dependency_app, name="dependency")


@app.command()
def create() -> None:
    id = get_next_task_id()
    typer.echo(f"Creating task [{id}]")
    task_register = load_task_register()
    task_hierarchies = load_task_hierarchies()
    task_dependencies = load_task_dependencies()

    task_register[id] = Task()
    task_hierarchies.add_node(id)
    task_dependencies.add_node(id)

    save_task_register(register=task_register)
    save_task_hierarchies(task_hierarchies=task_hierarchies)
    save_task_dependencies(task_dependencies=task_dependencies)

    increment_task_id_count()


@app.command()
def read(id: str) -> None:
    typer.echo(f"Reading task [{id}]")
    task_id = Id(id)

    task_register = load_task_register()

    task = task_register[task_id]

    typer.echo(f"Name: {task.name}")
    typer.echo(f"Description: {task.description}")
    typer.echo(f"Importance: {task.importance.value if task.importance else None}")
    typer.echo(f"Progress: {task.progress.value}")

    task_hierarchies = load_task_hierarchies()

    typer.echo("Parent tasks")
    for parent_id in task_hierarchies.predecessors(task_id):
        name = task_register[parent_id]
        typer.echo(f"- {parent_id}: {name}")

    typer.echo("Child tasks")
    for child_id in task_hierarchies.successors(task_id):
        name = task_register[child_id]
        typer.echo(f"- {child_id}: {name}")

    task_dependencies = load_task_dependencies()

    typer.echo("Blocking tasks")
    for blocking_id in task_dependencies.predecessors(task_id):
        name = task_register[blocking_id]
        typer.echo(f"- {blocking_id}: {name}")

    typer.echo("Blocked tasks")
    for blocked_id in task_dependencies.successors(task_id):
        name = task_register[blocked_id]
        typer.echo(f"- {blocked_id}: {name}")

    event_task_due_table = load_event_task_due_table()
    event_register = load_event_register()

    typer.echo("Events due by")
    for event_id in event_task_due_table.get_events(task_id):
        event_name = event_register[event_id]
        typer.echo(f"- {event_id}: {event_name}")


@app.command()
def ls() -> None:
    task_register = load_task_register()
    for id, task in task_register.items():
        typer.echo(f"{id}: {task.name}")
