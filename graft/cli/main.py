import typer

from graft.cli.event.event import app as event_app
from graft.cli.task.task import app as task_app
from graft.io import initialise

app = typer.Typer()
app.add_typer(typer_instance=task_app, name="task")
app.add_typer(typer_instance=event_app, name="event")


@app.command()
def init() -> None:
    """Initialise graft"""
    typer.echo("initialising graft")
    initialise()
