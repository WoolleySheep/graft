from collections.abc import MutableMapping

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.dependency_position_assignment.position import (
    DependencyLayers,
)


def get_dependency_positions_unnamed_method(
    graph: tasks.INetworkGraphView,
) -> dict[tasks.UID, DependencyLayers]:
    """Get the dependency positions of tasks.

    Rules:
    - min position (concrete tasks) == max(max position of upstream tasks) + 1
    - min position (non-concrete tasks) == min(min position of inferior tasks)
    - max position (concrete tasks) == min position
    - max position (non-concrete tasks)== max(max position of inferior tasks)
    """

    def get_min_position_recursive(
        task: tasks.UID,
        task_to_min_position_map: MutableMapping[tasks.UID, int],
        task_to_max_position_map: MutableMapping[tasks.UID, int],
        task_to_max_position_of_upstream_tasks_map: MutableMapping[
            tasks.UID, int | None
        ],
    ) -> int:
        if task in task_to_min_position_map:
            return task_to_min_position_map[task]

        if graph.hierarchy_graph().is_concrete(task):
            max_position_of_upstream_tasks = get_max_position_of_upstream_tasks_recursive(
                task,
                task_to_min_position_map=task_to_min_position_map,
                task_to_max_position_map=task_to_max_position_map,
                task_to_max_position_of_upstream_tasks_map=task_to_max_position_of_upstream_tasks_map,
            )
            tmp_min_position = (
                max_position_of_upstream_tasks + 1
                if max_position_of_upstream_tasks is not None
                else 0
            )
        else:
            tmp_min_position = min(
                get_min_position_recursive(
                    subtask,
                    task_to_min_position_map=task_to_min_position_map,
                    task_to_max_position_map=task_to_max_position_map,
                    task_to_max_position_of_upstream_tasks_map=task_to_max_position_of_upstream_tasks_map,
                )
                for subtask in graph.hierarchy_graph().subtasks(task)
            )

        task_to_min_position_map[task] = tmp_min_position
        return tmp_min_position

    def get_max_position_recursive(
        task: tasks.UID,
        task_to_min_position_map: MutableMapping[tasks.UID, int],
        task_to_max_position_map: MutableMapping[tasks.UID, int],
        task_to_max_position_of_upstream_tasks_map: MutableMapping[
            tasks.UID, int | None
        ],
    ) -> int:
        if task in task_to_max_position_map:
            return task_to_max_position_map[task]

        if graph.hierarchy_graph().is_concrete(task):
            tmp_max_position = get_min_position_recursive(
                task,
                task_to_min_position_map=task_to_min_position_map,
                task_to_max_position_map=task_to_max_position_map,
                task_to_max_position_of_upstream_tasks_map=task_to_max_position_of_upstream_tasks_map,
            )
        else:
            tmp_max_position = 0
            for subtask in graph.hierarchy_graph().subtasks(task):
                subtask_max_position = get_max_position_recursive(
                    subtask,
                    task_to_min_position_map=task_to_min_position_map,
                    task_to_max_position_map=task_to_max_position_map,
                    task_to_max_position_of_upstream_tasks_map=task_to_max_position_of_upstream_tasks_map,
                )
                tmp_max_position = max(tmp_max_position, subtask_max_position)

        task_to_max_position_map[task] = tmp_max_position
        return tmp_max_position

    def get_max_position_of_upstream_tasks_recursive(
        task: tasks.UID,
        task_to_min_position_map: MutableMapping[tasks.UID, int],
        task_to_max_position_map: MutableMapping[tasks.UID, int],
        task_to_max_position_of_upstream_tasks_map: MutableMapping[
            tasks.UID, int | None
        ],
    ) -> int | None:
        if task in task_to_max_position_of_upstream_tasks_map:
            return task_to_max_position_of_upstream_tasks_map[task]

        tmp_max_position_of_upstream_tasks: int | None = None
        for dependee_task in graph.dependency_graph().dependee_tasks(task):
            dependee_task_max_position = get_max_position_recursive(
                dependee_task,
                task_to_min_position_map=task_to_min_position_map,
                task_to_max_position_map=task_to_max_position_map,
                task_to_max_position_of_upstream_tasks_map=task_to_max_position_of_upstream_tasks_map,
            )
            tmp_max_position_of_upstream_tasks = (
                max(
                    tmp_max_position_of_upstream_tasks,
                    dependee_task_max_position,
                )
                if tmp_max_position_of_upstream_tasks is not None
                else dependee_task_max_position
            )

        for supertask in graph.hierarchy_graph().supertasks(task):
            max_position_of_upstream_tasks_of_supertask = get_max_position_of_upstream_tasks_recursive(
                supertask,
                task_to_min_position_map=task_to_min_position_map,
                task_to_max_position_map=task_to_max_position_map,
                task_to_max_position_of_upstream_tasks_map=task_to_max_position_of_upstream_tasks_map,
            )
            tmp_max_position_of_upstream_tasks = max(
                tmp_max_position_of_upstream_tasks,
                max_position_of_upstream_tasks_of_supertask,
                key=lambda x: (x is not None, x),
            )

        task_to_max_position_of_upstream_tasks_map[task] = (
            tmp_max_position_of_upstream_tasks
        )
        return tmp_max_position_of_upstream_tasks

    task_to_min_position_map = dict[tasks.UID, int]()
    task_to_max_position_map = dict[tasks.UID, int]()
    task_to_max_position_of_upstream_tasks_map = dict[tasks.UID, int | None]()
    return {
        task: DependencyLayers(
            min_=get_min_position_recursive(
                task,
                task_to_min_position_map=task_to_min_position_map,
                task_to_max_position_map=task_to_max_position_map,
                task_to_max_position_of_upstream_tasks_map=task_to_max_position_of_upstream_tasks_map,
            ),
            max_=get_max_position_recursive(
                task,
                task_to_min_position_map=task_to_min_position_map,
                task_to_max_position_map=task_to_max_position_map,
                task_to_max_position_of_upstream_tasks_map=task_to_max_position_of_upstream_tasks_map,
            ),
        )
        for task in graph.tasks()
    }
