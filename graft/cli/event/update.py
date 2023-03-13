import datetime as dt

import typer

from graft.io import load_event_register, save_event_register
from graft.objects.event import Description, Id, Name

app = typer.Typer()


@app.command()
def name(id: str, name: str) -> None:
    typer.echo(f"Updating event [{id}] name to [{name}]")
    id = Id(id)
    name = Name(name)
    event_register = load_event_register()

    event = event_register[id]

    event.name = name

    save_event_register(event_register)


@app.command()
def description(id: str, description: str) -> None:
    typer.echo(f"Updating event [{id}] description to [{description}]")
    id = Id(id)
    description = Description(description)
    event_register = load_event_register()

    event = event_register[id]

    event.description = description

    save_event_register(event_register)


@app.command()
def datetime(id: str, datetime: str) -> None:
    typer.echo(f"Updating event [{id}] datetime to [{datetime}]")
    id = Id(id)

    try:
        datetime = dt.datetime.strptime(datetime, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        typer.echo(f"datetime format of [{datetime}] is invalid")
        return

    event_register = load_event_register()

    event = event_register[id]

    event.datetime = datetime

    save_event_register(event_register)
