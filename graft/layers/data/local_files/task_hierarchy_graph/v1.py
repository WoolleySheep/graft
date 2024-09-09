import json
from collections.abc import Generator, Iterable

from graft import graphs
from graft.domain import tasks


def _encode_uid(uid: tasks.UID) -> str:
    """Encode UID."""
    return str(int(uid))


def _decode_uid(number: str) -> tasks.UID:
    """Decode UID."""
    return tasks.UID(int(number))


def _convert_task_relationships_to_dict(
    relationships: Iterable[tuple[tasks.UID, Iterable[tasks.UID]]],
) -> dict[str, list[str]]:
    """Encode relationships between task UIDs."""
    return {
        _encode_uid(task): [_encode_uid(related_task) for related_task in related_tasks]
        for (task, related_tasks) in relationships
    }


def _convert_dict_to_task_relationships(
    d: dict[str, list[str]],
) -> Generator[tuple[tasks.UID, Generator[tasks.UID, None, None]], None, None]:
    """Decode relationships between task UIDs."""
    for task, related_tasks in d.items():
        yield (
            _decode_uid(task),
            (_decode_uid(related_task) for related_task in related_tasks),
        )


def encode_hierarchy_graph(graph: tasks.IHierarchyGraphView) -> str:
    return json.dumps(
        graph.task_subtasks_pairs(), default=_convert_task_relationships_to_dict
    )


def decode_hierarchy_graph(text: str) -> tasks.HierarchyGraph:
    hierarchy_relationships = json.loads(
        text, object_hook=_convert_dict_to_task_relationships
    )
    return tasks.HierarchyGraph(
        reduced_dag=graphs.ReducedDirectedAcyclicGraph(
            bidict=graphs.BiDirectionalSetDict(forward=hierarchy_relationships)
        )
    )
