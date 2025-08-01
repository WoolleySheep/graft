from graft.domain.tasks.network_graph import (
    INetworkGraphView,
    NetworkGraph,
    NetworkSubgraphBuilder,
)
from graft.domain.tasks.progress import Progress
from graft.domain.tasks.system import ISystemView, SubsystemBuilder, System
from graft.domain.tasks.uid import UID


def get_incomplete_system(system: ISystemView) -> System:
    """Get a modified version of the system that only shows the incomplete elements.

    Completed tasks will be removed entirely. This means that non-concrete tasks that
    only have "completed" and "not started" subtasks will show as "not started", even
    though they technically are "in progress".
    """
    if not system:
        return System.empty()

    builder = SubsystemBuilder(system)
    added_tasks = builder.add_superior_subgraph(
        filter(
            lambda task: system.attributes_register()[task].progress
            is not Progress.COMPLETED,
            system.network_graph().hierarchy_graph().concrete_tasks(),
        )
    )
    for task in added_tasks:
        for dependent_task in (
            system.network_graph().dependency_graph().dependent_tasks(task)
        ):
            if dependent_task not in added_tasks:
                continue
            builder.add_dependency(task, dependent_task)
    return builder.build()


def get_inferior_subgraph(task: UID, graph: INetworkGraphView) -> NetworkGraph:
    """Get a modified version of the graph that only shows the inferior tasks.

    This means that importance inherited from superior tasks will be lost, and tasks
    that had incomplete upstream tasks can now be started.
    """
    builder = NetworkSubgraphBuilder(graph)
    builder.add_inferior_subgraph([task])
    return builder.build()


def get_superior_subgraph(task: UID, graph: INetworkGraphView) -> NetworkGraph:
    """Get a modified version of the graph that only shows the superior tasks.

    This means that progress inherited from inferior tasks will be lost, and tasks
    that had incomplete upstream tasks can now be started.
    """
    builder = NetworkSubgraphBuilder(graph)
    builder.add_superior_subgraph([task])
    return builder.build()


def get_component_system(task: UID, system: ISystemView) -> System:
    """Get a modified version of the sytem that only shows the task's component."""
    builder = SubsystemBuilder(system)
    builder.add_component_subgraph(task)
    return builder.build()
