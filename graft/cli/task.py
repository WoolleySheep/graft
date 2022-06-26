from datetime import datetime
from typing import Optional

import typer

from graft.constrained_graph import (
    DescendantError,
    EdgeDoesNotExistError,
    EdgeExistsError,
    EdgeIntroducesCycleError,
    NodeDoesNotExistError,
    SelfLoopError,
    SuccessorOfAncestorError,
)
from graft.draw import draw_x
from graft.duration import Duration
from graft.io import (
    get_next_task_uid,
    increment_task_uid_count,
    initialise_task_attributes_map,
    initialise_task_dependencies,
    initialise_task_hierarchy,
    initialise_task_uid_count,
    load_task_attributes_map,
    load_task_dependencies,
    load_task_hierarchy,
    load_task_tag_table,
    save_task_attributes_map,
    save_task_dependencies,
    save_task_hierarchy,
    save_task_tag_table,
)
from graft.priority import Priority
from graft.progress import Progress
from graft.task_attributes import (
    AfterDueDatetimeError,
    BeforeStartDatetimeError,
    NotStartedToCompletedError,
    TaskAttributes,
    TaskBlockedError,
    TaskCompletedError,
    TaskNotBlockedError,
)
from graft.task_network import (
    SuperiorTaskPrioritiesError,
    TaskDoesNotExistError,
    TaskNetwork,
)

app = typer.Typer()


@app.command()
def ls():
    """list tasks"""
    typer.echo("listing tasks")
    task_attributes_map = load_task_attributes_map()
    if not task_attributes_map:
        typer.echo("no tasks")
        return
    sorted_uid_attributes_pairs = sorted(
        task_attributes_map.items(), key=lambda x: x[0]
    )
    for uid, attributes in sorted_uid_attributes_pairs:
        typer.echo(f"{uid}: {attributes.name}")


@app.command()
def create():
    """create a new task"""
    # TODO: Allow name to be specified during creation
    uid = get_next_task_uid()
    typer.echo(f"creating a new task [{uid}]")
    task_attributes_map = load_task_attributes_map()
    task_hierarchy = load_task_hierarchy()
    task_dependencies = load_task_dependencies()

    task_attributes_map[uid] = TaskAttributes()
    task_hierarchy.add_node(uid)
    task_dependencies.add_node(uid)

    save_task_attributes_map(task_attributes_map=task_attributes_map)
    save_task_hierarchy(task_hierarchy=task_hierarchy)
    save_task_dependencies(task_dependencies=task_dependencies)

    increment_task_uid_count()


@app.command()
def name(uid: str, name: str):
    """set the name of a task"""
    # TODO: Decide whether to specify maximum length
    typer.echo(f"setting name of task [{uid}] to [{name}]")
    task_attributes_map = load_task_attributes_map()
    try:
        attributes = task_attributes_map[uid]
    except KeyError:
        typer.echo(f"task [{uid}] does not exist")
        return

    attributes.name = name

    save_task_attributes_map(task_attributes_map=task_attributes_map)


@app.command()
def description(uid: str, description: str):
    """set the description of a task"""
    typer.echo(f"setting description of task [{uid}] to [{description}]")
    task_attributes_map = load_task_attributes_map()
    try:
        attributes = task_attributes_map[uid]
    except KeyError:
        typer.echo(f"task [{uid}] does not exist")
        return

    attributes.description = description

    save_task_attributes_map(task_attributes_map=task_attributes_map)


@app.command()
def priority(uid: str, priority: Optional[Priority] = typer.Argument(default=None)):
    """set the priority of a task"""
    # TODO: Add more descriptive typer hints
    # TODO: Think of way to make 'clearing' behaviour more obvious
    # TODO: Decide whether to reject no-op assignments (eg: medium -> medium)
    if priority:
        typer.echo(f"setting priority of task [{uid}] to [{priority.value}]")
        task_attributes_map = load_task_attributes_map()
        task_hierarchy = load_task_hierarchy()
        task_dependencies = load_task_dependencies()
        task_network = TaskNetwork(
            task_attributes_map=task_attributes_map,
            task_hierarchy=task_hierarchy,
            task_dependencies=task_dependencies,
        )
        try:
            task_network.set_priority(uid=uid, priority=priority)
        except TaskDoesNotExistError:
            typer.echo(f"task [{uid}] does not exist")
            return
        except SuperiorTaskPrioritiesError as e:
            typer.echo(f"task [{uid}] has superior tasks with priorities:")
            for superior_uid in e.superior_tasks_with_priorities:
                superior_name = task_attributes_map[superior_uid].name
                superior_priority = task_attributes_map[superior_uid].priority
                typer.echo(
                    f"- {superior_uid}: [{superior_name}] - {superior_priority.value}"
                )
            return

    else:
        typer.echo(f"clearing priority of task [{uid}]")
        task_attributes_map = load_task_attributes_map()
        try:
            attributes = task_attributes_map[uid]
        except KeyError:
            typer.echo(f"task [{uid}] does not exist")
            return

        attributes.priority = None

    save_task_attributes_map(task_attributes_map=task_attributes_map)


@app.command()
def progress(uid: str, progress: Progress):
    """set the progress of a task"""
    typer.echo(f"setting progress of task [{uid}] to [{progress.value}]")
    task_hierarchy = load_task_hierarchy()
    try:
        is_concrete_task = task_hierarchy.is_leaf_node(node=uid)
    except NodeDoesNotExistError:
        typer.echo(f"task [{uid}] does not exist")
        return

    if not is_concrete_task:
        typer.echo("task is not a concrete task")
        return

    task_attributes_map = load_task_attributes_map()

    # TODO: Check if progress can be moved to this state
    try:
        task_attributes_map[uid].set_progress(progress=progress)
    except TaskBlockedError:
        typer.echo(f"task [{uid}] is blocked")
        return
    except NotStartedToCompletedError:
        typer.echo(f"task [{uid}] cannot be moved from 'not started' to 'completed'")
        return

    # TODO: Can't uncomplete a task if subsequent tasks have been started as a result

    save_task_attributes_map(task_attributes_map=task_attributes_map)


@app.command()
def duration(uid: str, duration: Optional[Duration] = typer.Argument(default=None)):
    """set the duration of a task"""
    # TODO: Restructure supertask to remove duration field
    if duration:
        typer.echo(f"setting duration of task [{uid}] to [{duration.value}]")
    else:
        typer.echo(f"clearing duration of task [{uid}]")

    task_hierarchy = load_task_hierarchy()
    if not task_hierarchy.is_leaf_node(node=uid):
        typer.echo(f"task [{uid}] is not a concrete task")
        return

    task_attributes_map = load_task_attributes_map()
    try:
        attributes = task_attributes_map[uid]
    except KeyError:
        typer.echo(f"task [{uid}] does not exist")
        return

    # TODO: Add conditionals to check if duration can be set
    attributes.duration = duration

    save_task_attributes_map(task_attributes_map=task_attributes_map)


@app.command()
def block(uid: str):
    """block a task"""
    # TODO: Allow a blocking reason to be specified
    # TODO: Decide if blocking will be allowed for non-concrete tasks
    typer.echo(f"blocking task [{uid}]")
    task_attributes_map = load_task_attributes_map()
    try:
        attributes = task_attributes_map[uid]
    except KeyError:
        typer.echo(f"task [{uid}] does not exist")
        return

    try:
        attributes.block()
    except TaskBlockedError:
        typer.echo(f"task [{uid}] is already blocked")
        return
    except TaskCompletedError:
        typer.echo(f"task [{uid}] is already completed")
        return

    save_task_attributes_map(task_attributes_map=task_attributes_map)


@app.command()
def unblock(uid: str):
    """unblock a task"""
    typer.echo(f"unblocking task [{uid}]")
    task_attributes_map = load_task_attributes_map()
    try:
        attributes = task_attributes_map[uid]
    except KeyError:
        typer.echo(f"task [{uid}] does not exist")
        return
    try:
        attributes.unblock()
    except TaskNotBlockedError:
        typer.echo(f"task [{uid}] is not blocked")
        return

    save_task_attributes_map(task_attributes_map=task_attributes_map)


@app.command()
def due(uid: str, due_datetime: Optional[str] = typer.Argument(default=None)):
    """set the due datetime of a task"""
    if due_datetime:
        typer.echo(f"setting due datetime of task [{uid}] to [{due_datetime}]")
        # TODO: Allow other datetime formats
        try:
            due_datetime = datetime.strptime(due_datetime, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            typer.echo(f"datetime format of [{due_datetime}] is invalid")
            return
    else:
        typer.echo(f"clearing due datetime of task [{uid}]")

    task_attributes_map = load_task_attributes_map()
    try:
        attributes = task_attributes_map[uid]
    except KeyError:
        typer.echo(f"task [{uid}] does not exist")
        return

    # TODO: Check if you can set this due date (blocked by other tasks)
    try:
        attributes.set_due_datetime(due_datetime=due_datetime)
    except BeforeStartDatetimeError as e:
        formatted_start_datetime = e.start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        formatted_due_datetime = e.due_datetime.strftime("%Y-%m-%d %H:%M:%S")
        typer.echo(
            f"due datetime [{formatted_due_datetime}] is before start datetime [{formatted_start_datetime}]"
        )
        return

    save_task_attributes_map(task_attributes_map=task_attributes_map)


@app.command()
def start(uid: str, start_datetime: Optional[str] = typer.Argument(default=None)):
    """set the start datetime of a task"""
    if start_datetime:
        typer.echo(f"setting start datetime of task [{uid}] to [{start_datetime}]")
        # TODO: Allow other datetime formats
        try:
            start_datetime = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            typer.echo(f"datetime format of [{start_datetime}] is invalid")
            return

    else:
        typer.echo(f"clearing start datetime of task [{uid}]")

    task_attributes_map = load_task_attributes_map()
    try:
        attributes = task_attributes_map[uid]
    except KeyError:
        typer.echo(f"task [{uid}] does not exist")
        return

    # TODO: Check if you can set this start date (blocked by other tasks)
    try:
        attributes.set_start_datetime(start_datetime=start_datetime)
    except AfterDueDatetimeError as e:
        formatted_start_datetime = e.start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        formatted_due_datetime = e.due_datetime.strftime("%Y-%m-%d %H:%M:%S")
        typer.echo(
            f"start datetime [{formatted_start_datetime}] is after due datetime [{formatted_due_datetime}]"
        )
        return

    save_task_attributes_map(task_attributes_map=task_attributes_map)


@app.command()
def delete(
    uid: str = typer.Argument(..., metavar="id", help="id of the task to delete")
):
    """delete a task"""
    typer.echo(f"deleting task [{uid}]")
    task_attributes_map = load_task_attributes_map()
    if uid not in task_attributes_map:
        typer.echo(f"task [{uid}] does not exist")
        return

    task_hierarchy = load_task_hierarchy()
    task_dependencies = load_task_dependencies()
    task_tag_table = load_task_tag_table()

    # TODO Add checks for various conditions - will need to check all before
    # deleting any
    del task_attributes_map[uid]
    task_hierarchy.remove_node(node=uid)
    task_dependencies.remove_node(node=uid)
    task_tag_table.remove_task(uid=uid)

    save_task_attributes_map(task_attributes_map=task_attributes_map)
    save_task_hierarchy(task_hierarchy=task_hierarchy)
    save_task_dependencies(task_dependencies=task_dependencies)
    save_task_tag_table(table=task_tag_table)


@app.command()
def sub(uid1: str, uid2: str):
    """make task 2 a subtask of task 1"""
    # TODO: Replace logic with task_network object
    typer.echo(f"making task [{uid2}] a subtask of task [{uid1}]")
    # TODO: Restructure supertask to remove progress field

    task_attributes_map = load_task_attributes_map()
    try:
        attributes = task_attributes_map[uid1]
    except KeyError:
        typer.echo(f"task [{uid1}] does not exist")
        return
    if attributes.progress and attributes.progress is not Progress.NOT_STARTED:
        typer.echo(f"task [{uid1}] is already started")
        return
    if attributes.duration:
        typer.echo(f"task [{uid1}] has a duration [{attributes.duration}]")
        return

    task_hierarchy = load_task_hierarchy()

    try:
        task_hierarchy.add_edge(source=uid1, target=uid2)
    except NodeDoesNotExistError as e:
        typer.echo(f"task [{e.node}] does not exist")
        return
    except SelfLoopError:
        typer.echo("task cannot be a subtask of itself")
    except EdgeExistsError:
        typer.echo(f"task [{uid2}] is already a subtask of [{uid1}]")
        return
    except DescendantError as e:
        typer.echo(
            f"tag [{uid2}] is already a subourdinate task of [{uid1}] along the following paths:"
        )
        for path in sorted(e.paths):
            formatted_path = " -> ".join((f"[{task}]" for task in path))
            typer.echo(f"- {formatted_path}")
        return
    except SuccessorOfAncestorError as e:
        typer.echo(
            f"task [{uid2}] is already a subtask of task [{uid1}]'s superior tasks:"
        )
        for superior_task in e.ancestors:
            typer.echo(f"- {superior_task}")
        return
    except EdgeIntroducesCycleError as e:
        typer.echo(
            f"making task [{uid2}] a subtask of task [{uid1}] creates a cycle along the following paths:"
        )
        for path in sorted(e.paths):
            formatted_path = " -> ".join((f"[{task}]" for task in path))
            typer.echo(f"- {formatted_path}")

    # Clear progress of task 1 (knowing the current progress not started)
    attributes.clear_progress()
    save_task_attributes_map(task_attributes_map=task_attributes_map)

    # TODO: Add non-hierarchy
    save_task_hierarchy(task_hierarchy=task_hierarchy)


@app.command()
def unsub(uid1: str, uid2: str):
    """remove task 2 as a subtask of task 1"""
    typer.echo(f"removing task [{uid2}] as a subtask of task [{uid1}]")

    task_hierarchy = load_task_hierarchy()

    try:
        task_hierarchy.remove_edge(source=uid1, target=uid2)
    except NodeDoesNotExistError as e:
        typer.echo(f"task [{e.node}] does not exist")
        return
    except SelfLoopError:
        typer.echo("task cannot be a subtask of itself")
    except EdgeDoesNotExistError:
        typer.echo(f"task [{uid2}] is not a subtask of [{uid1}]")
        return

    task_attributes_map = load_task_attributes_map()
    if not task_hierarchy.has_successors(node=uid1):
        task_attributes_map[uid1].set_progress(progress=Progress.NOT_STARTED)
        save_task_hierarchy(task_hierarchy=task_hierarchy)

    save_task_attributes_map(task_attributes_map=task_attributes_map)


@app.command()
def depend(uid1: str, uid2: str):
    """make task 2 dependent on task 1"""
    typer.echo(f"making task [{uid2}] dependent on [{uid1}]")

    task_dependencies = load_task_dependencies()

    # TODO: Many more conditions to consider
    try:
        task_dependencies.add_edge(source=uid1, target=uid2)
    except NodeDoesNotExistError as e:
        typer.echo(f"task [{e.node}] does not exist")
        return
    except SelfLoopError:
        typer.echo("task cannot be dependent on itself")
        return
    except EdgeExistsError:
        typer.echo(f"task [{uid2}] is already dependent on task [{uid2}]")
        return
    except DescendantError as e:
        typer.echo(
            f"task [{uid2}] is already a downstream task of [{uid1}] along the following paths:"
        )
        for path in sorted(e.paths):
            formatted_path = " -> ".join((f"[{task}]" for task in path))
            typer.echo(f"- {formatted_path}")
        return
    except SuccessorOfAncestorError as e:
        typer.echo(
            f"task [{uid2}] is already dependent on task [{uid1}]'s upstream tasks:"
        )
        for upstream_task in e.ancestors:
            typer.echo(f"- {upstream_task}")
        return
    except EdgeIntroducesCycleError as e:
        typer.echo(
            f"making task [{uid2}] dependent on task [{uid1}] creates a cycle along the following paths:"
        )
        for path in sorted(e.paths):
            formatted_path = " -> ".join((f"[{task}]" for task in path))
            typer.echo(f"- {formatted_path}")

    save_task_dependencies(task_dependencies=task_dependencies)


@app.command()
def undepend(uid1: str, uid2: str):
    """remove task 2 as a dependent of task 1"""
    typer.echo(f"removing task [{uid2}] as a dependent of task [{uid1}]")

    task_dependencies = load_task_dependencies()

    try:
        task_dependencies.remove_edge(source=uid1, target=uid2)
    except NodeDoesNotExistError as e:
        typer.echo(f"task [{e.node}] does not exist")
        return
    except SelfLoopError:
        typer.echo("task cannot be a connected to itself")
    except EdgeDoesNotExistError:
        typer.echo(f"task [{uid1}] is not connected to [{uid2}]")
        return

    save_task_dependencies(task_dependencies=task_dependencies)


@app.command()
def inspect(
    uid: str = typer.Argument(..., metavar="id", help="id of the task to read")
):
    """inspect a task"""
    typer.echo(f"inspecting task [{uid}]")
    task_attributes_map = load_task_attributes_map()

    if uid not in task_attributes_map:
        typer.echo(f"task [{uid}] does not exist")
        return

    task_hierarchy = load_task_hierarchy()

    typer.echo(f"name: {task_attributes_map[uid].name}")
    typer.echo(f"description: {task_attributes_map[uid].description}")
    typer.echo(
        f"priority: {task_attributes_map[uid].priority.value if task_attributes_map[uid].priority else None}"
    )

    # Non-concrete tasks cannot have their progress or duration set
    if task_hierarchy.is_leaf_node(node=uid):
        typer.echo(f"progress: {task_attributes_map[uid].progress.value}")
        typer.echo(
            f"duration: {task_attributes_map[uid].duration.value if task_attributes_map[uid].duration else None}"
        )

    typer.echo(f"blocked: {task_attributes_map[uid].blocked}")
    typer.echo(
        f"due datetime: {task_attributes_map[uid].due_datetime.strftime('%Y-%m-%d %H:%M:%S') if task_attributes_map[uid].due_datetime else None}"
    )
    typer.echo(
        f"start datetime: {task_attributes_map[uid].start_datetime.strftime('%Y-%m-%d %H:%M:%S') if task_attributes_map[uid].start_datetime else None}"
    )
    typer.echo(
        f"created datetime: {task_attributes_map[uid].created_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    typer.echo(
        f"started datetime: {task_attributes_map[uid].started_datetime.strftime('%Y-%m-%d %H:%M:%S') if task_attributes_map[uid].started_datetime else None}"
    )

    # TODO: Show network-dependent information
    #   - progress (non-concrete tasks)
    #   - Longest subourdinate task duration (non-concrete tasks)
    #   - Latest upstream task start datetime
    #   - Earliest upstream task due datetime
    #   - Superior task priorities
    #   - Active task status
    #   - etc

    task_hierarchy = load_task_hierarchy()

    typer.echo("supertasks")
    supertasks = list(task_hierarchy.predecessors(node=uid))
    if not supertasks:
        typer.echo("no supertasks")
    else:
        for supertask in sorted(supertasks):
            typer.echo(f"- {supertask}: {task_attributes_map[supertask].name}")

    typer.echo("subtasks")
    subtasks = list(task_hierarchy.successors(node=uid))
    if not subtasks:
        typer.echo("no subtasks")
    else:
        for subtask in sorted(subtasks):
            typer.echo(f"- {subtask}: {task_attributes_map[subtask].name}")

    task_dependencies = load_task_dependencies()

    # TODO: Need a better name than this
    typer.echo("dependee tasks")
    dependee_tasks = list(task_dependencies.predecessors(node=uid))
    if not dependee_tasks:
        typer.echo("no dependee tasks")
    else:
        for task in sorted(dependee_tasks):
            typer.echo(f"- {task}: {task_attributes_map[task].name}")

    typer.echo("dependent tasks")
    dependent_tasks = list(task_dependencies.successors(node=uid))
    if not dependent_tasks:
        typer.echo("no dependent tasks")
    else:
        for task in sorted(dependent_tasks):
            typer.echo(f"- {task}: {task_attributes_map[task].name}")

    task_tag_table = load_task_tag_table()
    typer.echo("tags")
    tags = list(task_tag_table.get_tags_for_a_task(uid=uid))
    if tags:
        for tag in sorted(tags):
            typer.echo(f"- {tag}")
    else:
        typer.echo("no tags")


@app.command()
def draw():
    """draw the task hierarchy and dependencies graphs"""
    typer.echo("drawing the task hierarchy and dependencies graphs")
    task_attributes_map = load_task_attributes_map()
    if not task_attributes_map:
        typer.echo("no tasks to draw")
        return
    task_hierarchy = load_task_hierarchy()
    task_dependencies = load_task_dependencies()
    # TODO: Find a better name
    draw_x(
        task_hierarchy_digraph=task_hierarchy,
        task_dependencies_digraph=task_dependencies,
        task_attributes_map=task_attributes_map,
    )


@app.command()
def erase():
    """erase tasks"""
    # TODO: Add options to just erase hierarchy or dependencies
    typer.echo("erasing tasks")
    initialise_task_attributes_map()
    initialise_task_hierarchy()
    initialise_task_dependencies()
    initialise_task_uid_count()
