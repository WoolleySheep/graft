import typer

from graft.cli.tag import app as tag_app
from graft.cli.task import app as task_app
from graft.io import (
    initialise_all,
    load_tag_hierarchy,
    load_task_attributes_map,
    load_task_dependencies,
    load_task_hierarchy,
)
from graft.ranking_algorithm import rank_tasks

DESCRIPTION_DISPLAY_CHAR_BUFFER = 10

app = typer.Typer()
app.add_typer(typer_instance=task_app, name="task")
app.add_typer(typer_instance=tag_app, name="tag")


@app.command()
def init():
    """Initialise graft"""
    typer.echo("initialising graft")
    # TODO: Don't initialise if already done
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


@app.command()
def search(query: str):
    """Search for matching tasks or tags.

    Matches with
    - Tasks whose name or description contains the query
    - Tags whose name contains the query
    """
    typer.echo(f"searching for tasks and tags matching [{query}]")
    tasks_matched_by_name = []
    tasks_matched_by_description = []
    task_attributes_map = load_task_attributes_map()
    for uid, attributes in task_attributes_map.items():
        if query in attributes.name:
            tasks_matched_by_name.append((uid, attributes.name))
        if query in attributes.description:
            tasks_matched_by_description.append(
                (uid, attributes.name, attributes.description)
            )

    typer.echo("tasks matched by name")
    if not tasks_matched_by_name:
        typer.echo("no tasks")
    else:
        for uid, name in sorted(tasks_matched_by_name, key=lambda x: int(x[0])):
            typer.echo(f"- {uid}: {name}")

    typer.echo("tasks matched by description")
    if not tasks_matched_by_description:
        typer.echo("no tasks")
    else:
        for uid, name, description in sorted(
            tasks_matched_by_description, key=lambda x: int(x[0])
        ):
            query_index = description.find(query)
            buffer = 10
            start = max(0, query_index - DESCRIPTION_DISPLAY_CHAR_BUFFER)
            start_chars = "..." if start > 0 else ""
            end = min(
                len(description),
                query_index + len(query) + DESCRIPTION_DISPLAY_CHAR_BUFFER + 1,
            )
            end_chars = "..." if end < len(description) else ""
            truncated_description = description[start:end]
            typer.echo(
                f"- {uid}: {name} - [{start_chars}{truncated_description}{end_chars}]"
            )

    tag_hierarchy = load_tag_hierarchy()
    tags_matched_by_name = []
    for tag in tag_hierarchy.nodes():
        if query in tag:
            tags_matched_by_name.append(tag)

    typer.echo("tags matched by name")
    if not tasks_matched_by_name:
        typer.echo("no tags")
    else:
        for tag in sorted(tags_matched_by_name):
            typer.echo(f"- {tag}")


# TODO: Add export command
# - Account for "." and associated manipulations

# TODO: Add erase command
