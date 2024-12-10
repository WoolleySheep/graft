import collections
from collections.abc import Generator, Mapping

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.dependency_position_assignment import (
    position as dependency_position,
)


class TaskRelationLayers:
    """The layers of the task cylinder resulting from its hierarchy and dependency relationships."""

    def __init__(
        self,
        dependency_layers: dependency_position.DependencyLayers,
        hierarchy_layer: int,
    ) -> None:
        self._dependency = dependency_layers
        self._hierarchy = hierarchy_layer

    @property
    def dependency(self) -> dependency_position.DependencyLayers:
        return self._dependency

    @property
    def hierarchy(self) -> int:
        return self._hierarchy

    def __repr__(self) -> str:
        return f"TaskRelationLayers(dependency={self.dependency}, hierarchy={self.hierarchy})"


def get_hierarchy_layers_in_descending_order(
    task_to_relation_layers_map: Mapping[tasks.UID, TaskRelationLayers],
) -> Generator[set[tasks.UID], None, None]:
    """Get the hierarchy layers in descending order.

    A convenience function for converting a dict of relation layers back into a list format.
    """
    hierarchy_layer_to_tasks_map = collections.defaultdict[int, set[tasks.UID]](set)
    for task, relation_layers in task_to_relation_layers_map.items():
        hierarchy_layer_to_tasks_map[relation_layers.hierarchy].add(task)

    for layer in sorted(hierarchy_layer_to_tasks_map.keys(), reverse=True):
        yield hierarchy_layer_to_tasks_map[layer]
