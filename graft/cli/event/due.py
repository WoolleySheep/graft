import typer

import graft.objects.event as event
import graft.objects.task as task
from graft.io import load_event_task_due_table, save_event_task_due_table

app = typer.Typer()


@app.command()
def create(task_id: str, event_id) -> None:
    typer.echo(f"Creating due requirement - task [{task_id}] due by event [{event_id}]")
    task_id = task.Id(task_id)
    event_id = event.Id(event_id)

    event_task_due_table = load_event_task_due_table()

    event_task_due_table.add(event_id, task_id)

    save_event_task_due_table(event_task_due_table)


@app.command()
def delete(task_id: str, event_id: str) -> None:
    typer.echo(
        f"Deleting due requirement - task [{task_id}] is not due by event [{event_id}]"
    )

    task_id = task.Id(task_id)
    event_id = event.Id(event_id)

    event_task_due_table = load_event_task_due_table()

    event_task_due_table.remove(event_id, task_id)

    save_event_task_due_table(event_task_due_table)
