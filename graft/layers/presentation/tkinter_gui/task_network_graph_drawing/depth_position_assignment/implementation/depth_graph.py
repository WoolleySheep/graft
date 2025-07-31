import itertools
from collections.abc import Iterable, Mapping

from graft import graphs
from graft.domain import tasks
from graft.graphs.directed_graph_builder import DirectedGraphBuilder


def get_constrained_depth_graph(
    task_groups_along_dependency_axis: Iterable[Iterable[tasks.UID]],
    task_to_depth_index_map: Mapping[tasks.UID, int],
) -> graphs.DirectedAcyclicGraph[tasks.UID]:
    """Return a fully constrained depth graph.

    Requires that the task groups and depth indexes are known such that tasks
    can be laid out without any overlap.
    """
    graph_builder = DirectedGraphBuilder[tasks.UID]()
    for task_group in task_groups_along_dependency_axis:
        # Assumption: All tasks in the group have a different depth index
        tasks_sorted_by_depth = sorted(
            task_group, key=lambda task: (task_to_depth_index_map[task], task)
        )
        for task in tasks_sorted_by_depth:
            graph_builder.add_node(task)

        for shallower_task, deeper_task in itertools.pairwise(tasks_sorted_by_depth):
            graph_builder.add_edge(shallower_task, deeper_task)

    return graphs.DirectedAcyclicGraph(graph_builder.build().items())
