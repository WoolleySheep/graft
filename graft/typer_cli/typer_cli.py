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
