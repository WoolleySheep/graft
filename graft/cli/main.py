import typer

from graft.cli.tag import app as tag_app
from graft.cli.task import app as task_app
from graft.io import (
    initialise_all,
    load_task_attributes_map,
    load_task_dependencies,
    load_task_hierarchy,
)
from graft.ranking_algorithm import rank_tasks

app = typer.Typer()
app.add_typer(typer_instance=task_app, name="task")
app.add_typer(typer_instance=tag_app, name="tag")


@app.command()
def init():
    """Initialise graft"""
    typer.echo("initialising graft")
    initialise_all()


@app.command()
def rank():
    """Rank all tasks"""
    typer.echo("ranking tasks")
    task_attributes_map = load_task_attributes_map()
    task_hierarchy = load_task_hierarchy()
    task_dependencies = load_task_dependencies()

    ranked_tasks = rank_tasks(task_attributes_map, task_hierarchy, task_dependencies)
    if not ranked_tasks:
        typer.echo("no tasks")
    else:
        for uid in ranked_tasks:
            typer.echo(f"- {uid}: {task_attributes_map[uid].name}")
