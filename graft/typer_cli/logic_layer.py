import functools

from graft import architecture

logic_layer: architecture.LogicLayer | None = None


def assert_logic_layer_initialised(fn):
    """Check that the logic layer is initialised."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        assert logic_layer is not None
        return fn(*args, **kwargs)

    return wrapper
