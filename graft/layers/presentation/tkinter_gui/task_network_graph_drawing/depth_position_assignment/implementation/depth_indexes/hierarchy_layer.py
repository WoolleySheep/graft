from collections.abc import Mapping, MutableMapping, Sequence, Set

from graft.domain import tasks


class HierarchyLayer:
    """Convenience function for holding information relevant to a hierarchy layer"""

    def __init__(
        self,
        task_to_depth_index_map: MutableMapping[tasks.UID, int],
        task_to_dependency_midpoint_map: Mapping[tasks.UID, float],
        dependency_groups: Sequence[Set[tasks.UID]],
    ) -> None:
        self.task_to_depth_index_map = task_to_depth_index_map
        self.task_to_dependency_midpoint_map = task_to_dependency_midpoint_map
        self.dependency_groups = dependency_groups

    @property
    def tasks(self) -> tasks.TasksView:
        return tasks.TasksView(self.task_to_dependency_midpoint_map.keys())
