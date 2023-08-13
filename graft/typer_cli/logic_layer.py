import functools
from collections.abc import Callable
from typing import ParamSpec, TypeVar

from graft import architecture

T = TypeVar("T")
P = ParamSpec("P")

logic_layer: architecture.LogicLayer | None = None


class LogicLayerNotInitialisedError(Exception):
    """Raised when logic layer is not initialised."""


def check_logic_layer_initialised(fn: Callable[P, T]) -> Callable[P, T]:
    """Check that the logic layer is initialised."""

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if logic_layer is None:
            raise LogicLayerNotInitialisedError
        return fn(*args, **kwargs)

    return wrapper
