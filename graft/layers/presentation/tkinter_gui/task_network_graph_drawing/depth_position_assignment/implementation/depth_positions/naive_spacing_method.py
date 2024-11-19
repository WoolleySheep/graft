from collections.abc import Mapping

from graft.domain import tasks


def get_depth_positions_naive_spacing_method(
    task_to_depth_index_map: Mapping[tasks.UID, int],
    separation_distance: float,
) -> dict[tasks.UID, float]:
    return {
        task: depth_index * separation_distance
        for task, depth_index in task_to_depth_index_map.items()
    }
