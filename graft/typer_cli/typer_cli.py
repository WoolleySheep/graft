"""Typer CLI presentation-layer implementation and associated exceptions."""

import typer

from graft import architecture
from graft.typer_cli import global_logic_layer, task

_app = typer.Typer()
_app.add_typer(typer_instance=task.app, name="task", help="Task management commands.")


def run_app(logic_layer: architecture.LogicLayer) -> None:
    """Run Typer CLI app."""
    global_logic_layer.set_logic_layer(layer=logic_layer)
    _app()


@_app.command()
def erase() -> None:
    """Erase all data."""
    typer.echo("Erasing all data")
    try:
        logic_layer = global_logic_layer.get_logic_layer()
        logic_layer.erase()
    except Exception as e:
        typer.echo(f"Failed to erase; exception [{e}] raised")
        raise
    typer.echo("Erased all data")
