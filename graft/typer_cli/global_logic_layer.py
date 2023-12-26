"""Module for sharing global logic layer initialisation state."""

import functools
from collections.abc import Callable

from graft import architecture

# The reason for using this global logic layer is to make the concept of a
# layered architecture play nice with the fact that typer registers functions as
# commands. This was the best work-around I could find.
_global_logic_layer: architecture.LogicLayer | None = None


class LogicLayerNotInitialisedError(Exception):
    """Raised when logic layer is not initialised."""


def set_logic_layer(layer: architecture.LogicLayer) -> None:
    """Set the global logic layer."""
    global _global_logic_layer
    _global_logic_layer = layer


def get_logic_layer() -> architecture.LogicLayer:
    """Get the global logic layer."""
    if _global_logic_layer is None:
        raise LogicLayerNotInitialisedError

    return _global_logic_layer


def check_initialised[T, **P](fn: Callable[P, T]) -> Callable[P, T]:
    """Check that the global logic layer is initialised."""

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if _global_logic_layer is None:
            raise LogicLayerNotInitialisedError
        return fn(*args, **kwargs)

    return wrapper
