import abc

from graft.architecture import data


class LogicLayer(abc.ABC):
    """Logic layer interface."""

    def __init__(self, data_layer: data.DataLayer) -> None:
        """Initialize logic layer."""
        self.data_layer = data_layer
