from typing import Optional

import typer

from graft.constrained_graph import (
    DescendantError,
    EdgeDoesNotExistError,
    EdgeExistsError,
    EdgeIntroducesCycleError,
    NodeDoesNotExistError,
    NodeExistsError,
    PredecessorsError,
    SelfLoopError,
    SuccessorOfAncestorError,
    SuccessorsError,
)
from graft.draw import draw_y
from graft.io import (
    initialise_tag_hierarchy,
    initialise_task_tag_table,
    load_tag_hierarchy,
    load_task_attributes_map,
    load_task_tag_table,
    save_tag_hierarchy,
    save_task_tag_table,
)
from graft.task_tag_table import TaskTagPairDoesNotExistError, TaskTagPairExistsError

app = typer.Typer()


@app.command()
def ls(tags: bool = typer.Option(True, "--tags/--dependencies")):
    """List all tags or all dependencies"""
    typer.echo(f"listing {'tags' if tags else 'dependencies'}")
    tag_hierarchy = load_tag_hierarchy()
    if tags:
        if not tag_hierarchy:
            typer.echo("no tags")
            return
        for tag in sorted(tag_hierarchy.nodes()):
            typer.echo(f"- {tag}")
    else:
        dependencies = list(tag_hierarchy.edges())
        if not dependencies:
            typer.echo("no dependencies")
            return
        for name1, name2 in sorted(dependencies):
            typer.echo(f"- [{name1}] -> [{name2}]")


@app.command()
def create(name: str):
    """
    Create a new tag
    """
    # TODO: Add name validation
    typer.echo(f"creating tag [{name}]")

    tag_hierarchy = load_tag_hierarchy()

    try:
        tag_hierarchy.add_node(node=name)
    except NodeExistsError:
        typer.echo(f"tag [{name}] already exists")
        return

    save_tag_hierarchy(tag_hierarchy=tag_hierarchy)


@app.command()
def delete(name: str, link: Optional[bool] = typer.Option(None, "--re-link/--un-link")):
    """
    Delete a tag
    """

    # TODO: Handle case where tag is affixed to task(s)

    tag_hierarchy = load_tag_hierarchy()
    try:
        if link is None:
            typer.echo(f"deleting tag [{name}]")
            try:
                tag_hierarchy.remove_node(node=name)
            except PredecessorsError as e:
                typer.echo(f"tag [{name}] has supertags:")
                for node in sorted(e.predecessors):
                    typer.echo(f"- {node}")
                return
            except SuccessorsError as e:
                typer.echo(f"tag [{name}] has subtags:")
                for node in sorted(e.successors):
                    typer.echo(f"- {node}")
                return
        elif link:
            typer.echo("deleting tag and re-linking neighbouring tags")
            tag_hierarchy.remove_node_and_create_edges_from_predecessors_to_successors(
                node=name
            )
        else:
            typer.echo("deleting tag and associated links")
            tag_hierarchy.remove_node_and_neighbouring_edges(node=name)
    except NodeDoesNotExistError:
        typer.echo(f"tag [{name}] does not exist")
        return

    save_tag_hierarchy(tag_hierarchy=tag_hierarchy)


@app.command()
def inspect(name: str):
    """
    Inspect a tag
    """
    typer.echo(f"inspecting tag [{name}]")

    tag_hierarchy = load_tag_hierarchy()

    try:
        supertags = list(tag_hierarchy.predecessors(node=name))
        typer.echo("supertags")
        if supertags:
            for supertag in sorted(supertags):
                typer.echo(f"- {supertag}")
        else:
            typer.echo("no supertags")

        typer.echo("subtags")
        subtags = list(tag_hierarchy.successors(node=name))
        if subtags:
            for subtag in sorted(subtags):
                typer.echo(f"- {subtag}")
        else:
            typer.echo("no subtags")

    except NodeDoesNotExistError:
        typer.echo(f"tag [{name}] does not exist")
        return

    task_tag_table = load_task_tag_table()
    typer.echo("tasks")
    tasks = list(task_tag_table.get_tasks_for_a_tag(name=name))
    if tasks:
        task_attributes_map = load_task_attributes_map()
        for task in sorted(tasks):
            name = task_attributes_map[task].name
            typer.echo(f"- {task}: {name}")
    else:
        typer.echo("no tasks")


@app.command()
def rename(
    old_name: str = typer.Argument(..., help="Old name of the tag"),
    new_name: str = typer.Argument(..., help="New name for the tag"),
):
    """
    Rename a tag
    """
    # TODO: Add name validation
    typer.echo(f"Renaming tag [{old_name}] to [{new_name}]")

    # TODO: Fix inefficiency of doing task-tag work before checking if tag exists
    task_tag_table = load_task_tag_table()
    task_tag_table.rename_tag(old_name=old_name, new_name=new_name)

    tag_hierarchy = load_tag_hierarchy()
    tag_hierarchy.mimic = True
    try:
        tag_hierarchy.relabel_node(old_label=old_name, new_label=new_name)
    except NodeDoesNotExistError:
        typer.echo(f"tag [{old_name}] does not exist")
        return
    except NodeExistsError:
        typer.echo(f"tag [{new_name}] already exists")
        return
    finally:
        tag_hierarchy.mimic = False

    save_task_tag_table(table=task_tag_table)
    save_tag_hierarchy(tag_hierarchy=tag_hierarchy)


@app.command()
def affix(uid: str, name: str):
    """
    Affix a tag to a task
    """
    typer.echo(f"affixing tag [{name}] to task [{uid}]")

    tag_hierarchy = load_tag_hierarchy()
    if name not in tag_hierarchy:
        typer.echo(f"tag [{name}] does not exist")
        return

    task_attributes_map = load_task_attributes_map()
    if uid not in task_attributes_map:
        typer.echo(f"task [{uid}] does not exist")
        return

    task_tag_table = load_task_tag_table()

    # TODO: Additional checks
    #   - Superior tag already affixed
    #   - Subourdinate tag already affixed
    # TODO: Consider combined tag and task hierarchy interactions
    try:
        task_tag_table.add_task_tag_pair(task_uid=uid, tag_name=name)
    except TaskTagPairExistsError:
        typer.echo(f"tag [{name}] is already affixed to task [{uid}]")
        return

    save_task_tag_table(table=task_tag_table)


@app.command()
def unfix(uid: str, name: str):
    """
    Remove a tag from a task
    """
    typer.echo(f"unfixing tag [{name}] from task [{uid}]")

    tag_hierarchy = load_tag_hierarchy()
    if name not in tag_hierarchy:
        typer.echo(f"tag [{name}] does not exist")
        return

    task_attributes_map = load_task_attributes_map()
    if uid not in task_attributes_map:
        typer.echo(f"task [{uid}] does not exist")
        return

    task_tag_table = load_task_tag_table()

    try:
        task_tag_table.remove_task_tag_pair(task_uid=uid, tag_name=name)
    except TaskTagPairDoesNotExistError:
        typer.echo(f"tag [{name}] is not affixed to task [{uid}]")
        return

    save_task_tag_table(table=task_tag_table)


@app.command()
def draw():
    """
    Draw the tag hierarchy
    """
    # TODO: Add task-tag pairs to drawing
    # Add a second pane to the right with the task-tag pairs
    # Two columns - tags on one site, tasks on the other
    typer.echo("drawing the tag hierarchy")
    tag_hierarchy = load_tag_hierarchy()

    if not tag_hierarchy:
        typer.echo("no tags")
        return

    task_tag_table = load_task_tag_table()
    task_attributes_map = load_task_attributes_map()

    draw_y(
        tag_hierarchy=tag_hierarchy,
        task_tag_table=task_tag_table,
        task_attributes_map=task_attributes_map,
    )


@app.command()
def sub(
    name1: str,
    name2: str,
):
    """Make tag 2 a subtag of tag 1"""
    typer.echo(f"make tag [{name2}] a subtag of tag [{name1}]")

    tag_hierarchy = load_tag_hierarchy()

    try:
        tag_hierarchy.add_edge(source=name1, target=name2)
    except NodeDoesNotExistError as e:
        typer.echo(f"tag [{e.node}] does not exist")
        return
    except SelfLoopError:
        typer.echo("tag cannot be a subtag of itself")
    except EdgeExistsError:
        typer.echo(f"tag [{name2}] is already a subtag of [{name1}]")
        return
    except DescendantError as e:
        typer.echo(
            f"tag [{name2}] is already a subourdinate tag of [{name1}] along the following paths:"
        )
        for path in sorted(e.paths):
            formatted_path = " -> ".join((f"[{tag}]" for tag in path))
            typer.echo(f"- {formatted_path}")
        return
    except SuccessorOfAncestorError as e:
        typer.echo(
            f"tag [{name2}] is already a subtag of tag [{name1}]'s superior tags:"
        )
        for superior_tag in e.ancestors:
            typer.echo(f"- {superior_tag}")
        return
    except EdgeIntroducesCycleError as e:
        typer.echo(
            f"incorporating tag [{name2}] into tag [{name1}] creates a cycle along the following paths:"
        )
        for path in sorted(e.paths):
            formatted_path = " -> ".join((f"[{tag}]" for tag in path))
            typer.echo(f"- {formatted_path}")

    save_tag_hierarchy(tag_hierarchy=tag_hierarchy)


@app.command()
def unsub(name1: str, name2: str):
    """Remove tag 2 as a subtag of tag 1"""
    typer.echo(f"removing tag [{name2}] as a subtag of tag [{name1}]")

    tag_hierarchy = load_tag_hierarchy()

    try:
        tag_hierarchy.remove_edge(source=name1, target=name2)
    except NodeDoesNotExistError as e:
        typer.echo(f"tag [{e.node}] does not exist")
        return
    except SelfLoopError:
        typer.echo("tag cannot be a subtag of itself")
    except EdgeDoesNotExistError:
        typer.echo(f"tag [{name2}] is not a subtag of [{name1}]")
        return

    save_tag_hierarchy(tag_hierarchy=tag_hierarchy)


@app.command()
def erase(flag: bool = typer.Option(True, "--all/--dependencies")):
    """
    Erase the tag hierarchy
    """
    # TODO: Add option to just delete task-tag pairs
    if flag:
        typer.echo("erasing all tags")
        initialise_tag_hierarchy()
        initialise_task_tag_table()
    else:
        typer.echo("erasing all dependencies")
        tag_hierarchy = load_tag_hierarchy()
        tag_hierarchy.clear_edges()
        save_tag_hierarchy(tag_hierarchy=tag_hierarchy)


@app.command()
def ls_pairs():
    """List all task-tag pairs"""
    # TODO: Make this an option for the ls command
    typer.echo("listing task-tag pairs")
    task_tag_table = load_task_tag_table()
    if not task_tag_table:
        typer.echo("no task-tag pairs")
        return
    task_attributes_map = load_task_attributes_map()
    for task, tag in sorted(task_tag_table.data):
        typer.echo(f"- [{task}: {task_attributes_map[task].name}] - [{tag}]")


def is_tag_name_valid(name: str) -> bool:
    """
    Check if a tag name is valid
    """
    return "," not in name
