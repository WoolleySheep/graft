import abc

from graft.architecture import logic


class PresentationLayer(abc.ABC):
    """Presentation layer interface."""

    def __init__(self, logic_layer: logic.LogicLayer) -> None:
        """Initialise presentation layer."""
        self.logic_layer = logic_layer
