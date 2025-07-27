from graft.domain.tasks.progress import Progress
from graft.domain.tasks.system import ISystemView, SubsystemBuilder, System


def get_incomplete_system(system: ISystemView) -> System:
    """Get a modified version of the system that only shows the incomplete elements.

    Completed tasks will be removed entirely. This means that non-concrete tasks that
    only have "completed" and "not started" subtasks will show as "not started", even
    though they technically are "in progress".
    """
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
