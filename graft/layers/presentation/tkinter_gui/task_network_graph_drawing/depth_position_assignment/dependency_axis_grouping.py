import collections
from collections.abc import Collection, Generator, Mapping

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.task_layers import (
    TaskRelationLayers,
)


class TaskGroupAlongDependencyAxis:
    def __init__(self, position: int, task_group: set[tasks.UID]) -> None:
        self.position = position
        self.tasks = task_group


def get_dependency_axis_groups(
    tasks_: Collection[tasks.UID],
    task_to_relation_layers_map: Mapping[tasks.UID, TaskRelationLayers],
) -> Generator[set[tasks.UID], None, None]:
    """Get the groups of tasks at each hierarchy/depth plane slice of the dependency axis.

    That probably didn't make much sense. Consider his example:
    - A starts at 1 & ends at 3
    - B starts at 2 & ends at 2
    - C starts at 2 & ends at 4.

    Groups would be: {A}, {A, B, C}, {A, C}
    """
    min_dependency_position_to_task_map = collections.defaultdict[int, set[tasks.UID]](
        set
    )
    max_dependency_position_to_task_map = collections.defaultdict[int, set[tasks.UID]](
        set
    )
    for task in tasks_:
        task_dependency_position = task_to_relation_layers_map[task].dependency
        min_dependency_position_to_task_map[task_dependency_position.min].add(task)
        max_dependency_position_to_task_map[task_dependency_position.max].add(task)

    min_dependency_position_groups = (
        TaskGroupAlongDependencyAxis(position=position, task_group=task_group)
        for position, task_group in min_dependency_position_to_task_map.items()
    )
    sorted_min_dependency_position_groups = collections.deque(
        sorted(min_dependency_position_groups, key=lambda group: group.position)
    )

    max_dependency_position_groups = (
        TaskGroupAlongDependencyAxis(position=position, task_group=task_group)
        for position, task_group in max_dependency_position_to_task_map.items()
    )
    sorted_max_dependency_position_groups = collections.deque(
        sorted(max_dependency_position_groups, key=lambda group: group.position)
    )

    previous_position_task_group = set[tasks.UID]()

    while sorted_min_dependency_position_groups:
        starting_tasks_group = sorted_min_dependency_position_groups.popleft()

        task_group = previous_position_task_group | starting_tasks_group.tasks

        # Don't have to check that this queue is empty, as max positions should
        # never be empty while min positions is not empty
        while (
            sorted_max_dependency_position_groups[0].position
            < starting_tasks_group.position
        ):
            ended_tasks = sorted_max_dependency_position_groups.popleft()
            for task in ended_tasks.tasks:
                task_group.remove(task)

        yield task_group

        previous_position_task_group = task_group
