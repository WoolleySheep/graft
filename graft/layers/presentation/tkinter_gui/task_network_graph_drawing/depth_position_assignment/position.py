from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.dependency_position_assignment import (
    position as dependency_position,
)


class RelationPosition:
    """The position of the task cylinder resulting from its hierarchy and dependency relationships."""

    def __init__(
        self,
        dependency_position: dependency_position.DependencyPosition,
        hierarchy_position: int,
    ) -> None:
        self._dependency = dependency_position
        self._hierarchy = hierarchy_position

    @property
    def dependency(self) -> dependency_position.DependencyPosition:
        return self._dependency

    @property
    def hierarchy(self) -> int:
        return self._hierarchy
