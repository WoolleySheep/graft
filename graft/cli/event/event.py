import typer

from graft.cli.event.due import app as due_app
from graft.cli.event.update import app as update_app
from graft.io import (
    get_next_event_id,
    increment_event_id_count,
    load_event_register,
    load_event_task_due_table,
    load_task_register,
    save_event_register,
)
from graft.objects.event import Event, Id

app = typer.Typer()

app.add_typer(typer_instance=due_app, name="due")
app.add_typer(typer_instance=update_app, name="update")


@app.command()
def create() -> None:
    id = get_next_event_id()
    typer.echo(f"Creating event [{id}]")
    event_register = load_event_register()

    event_register[id] = Event()

    save_event_register(event_register)

    increment_event_id_count()


@app.command()
def read(id: str) -> None:
    typer.echo(f"Reading event [{id}]")
    event_id = Id(id)

    event_register = load_event_register()

    event = event_register[event_id]

    typer.echo(f"Name: {event.name}")
    typer.echo(f"Description: {event.description}")
    formatted_datetime = (
        event.datetime.strftime("%Y-%m-%d %H:%M:%S") if event.datetime else None
    )
    typer.echo(f"Datetime: {formatted_datetime}")

    event_task_due_table = load_event_task_due_table()
    task_register = load_task_register()

    typer.echo("Tasks due at")
    for task_id in event_task_due_table.get_tasks(event_id):
        task_name = task_register[task_id]
        typer.echo(f"- {task_id}: {task_name}")


@app.command()
def ls() -> None:
    event_register = load_event_register()
    for id, event in event_register.items():
        typer.echo(f"{id}: {event.name}")
