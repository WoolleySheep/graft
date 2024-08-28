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


def encode_dependency_graph(graph: tasks.IDependencyGraphView) -> str:
    return json.dumps(
        graph.task_dependents_pairs(), default=_convert_task_relationships_to_dict
    )


def decode_dependency_graph(text: str) -> tasks.DependencyGraph:
    dependency_relationships = json.loads(
        text, object_hook=_convert_dict_to_task_relationships
    )
    return tasks.DependencyGraph(
        dag=graphs.DirectedAcyclicGraph(
            bidict=graphs.BiDirectionalSetDict(forward=dependency_relationships)
        )
    )
