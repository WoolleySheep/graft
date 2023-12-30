"""Local file data-layer implementation and associated exceptions."""

import json
import pathlib
from typing import Final, TypedDict, override

from graft import architecture, domain, graphs
from graft.domain import tasks

_DATA_DIRECTORY_NAME: Final = "data"

_TASK_HIERARCHY_GRAPH_FILENAME: Final = "task_hierarchy_graph.json"
_TASK_DEPENDENCY_GRAPH_FILENAME: Final = "task_dependency_graph.json"
_TASK_ATTRIBUTES_REGISTER_FILENAME: Final = "task_attributes_register.json"
_TASK_NEXT_UID_FILENAME: Final = "task_next_uid.txt"

_DATA_DIRECTORY_PATH = pathlib.Path.cwd() / _DATA_DIRECTORY_NAME

_TASK_HIERARCHY_GRAPH_FILEPATH: Final = (
    _DATA_DIRECTORY_PATH / _TASK_HIERARCHY_GRAPH_FILENAME
)
_TASK_DEPENDENCY_GRAPH_FILEPATH: Final = (
    _DATA_DIRECTORY_PATH / _TASK_DEPENDENCY_GRAPH_FILENAME
)
_TASK_ATTRIBUTES_REGISTER_FILEPATH: Final = (
    _DATA_DIRECTORY_PATH / _TASK_ATTRIBUTES_REGISTER_FILENAME
)
_TASK_NEXT_UID_FILEPATH: Final = _DATA_DIRECTORY_PATH / _TASK_NEXT_UID_FILENAME


class TaskAttributesJSONDict(TypedDict):
    """Dictionary representation of Task Attributes in JSON format."""

    name: str | None
    description: str | None


def _encode_task_uid(uid: tasks.UID) -> str:
    """Encode task UID."""
    return str(uid)


def _decode_task_uid(number: str) -> tasks.UID:
    """Decode task UID."""
    return tasks.UID(int(number))


def _encode_task_uids(uids: tasks.UIDsView) -> list[str]:
    """Encode a collection of task UIDs."""
    return [_encode_task_uid(uid) for uid in uids]


def _decode_task_uids(numbers: list[str]) -> set[tasks.UID]:
    """Decode a collection of task UIDs."""
    return {_decode_task_uid(number) for number in numbers}


def _encode_task_attributes_register(
    o: tasks.AttributesRegisterView,
) -> dict[str, TaskAttributesJSONDict]:
    """Encode task attributes register."""

    def encode_attributes(attributes: tasks.AttributesView) -> TaskAttributesJSONDict:
        return {
            "name": str(attributes.name) if attributes.name is not None else None,
            "description": str(attributes.description)
            if attributes.description is not None
            else None,
        }

    if isinstance(o, tasks.AttributesRegisterView):
        return {
            _encode_task_uid(uid): encode_attributes(attributes)
            for uid, attributes in o.items()
        }

    raise TypeError


def _decode_task_attributes_register(
    d: dict,
) -> tasks.AttributesRegister | dict:
    """Decode task register.

    This function will be called on all dictionaries. If it is not the right
    format, return the original dictionary.
    """

    def decode_attributes(d: TaskAttributesJSONDict) -> tasks.Attributes:
        """Decode task attributes."""
        if "name" not in d or "description" not in d:
            raise ValueError  # TODO (mjw): Use better named error

        return tasks.Attributes(
            name=tasks.Name(d["name"]) if d["name"] is not None else None,
            description=(
                tasks.Description(d["description"])
                if d["description"] is not None
                else None
            ),
        )

    try:
        return tasks.AttributesRegister(
            task_to_attributes_map={
                _decode_task_uid(number): decode_attributes(attributes_dict)
                for number, attributes_dict in d.items()
            }
        )
    except ValueError:
        return d


def _encode_task_hierarchy_graph(
    hierarchy_graph_view: tasks.HierarchyGraphView,
) -> dict[str, list[str]]:
    """Encode task hierarchy graph."""
    if isinstance(hierarchy_graph_view, tasks.HierarchyGraphView):
        return {
            _encode_task_uid(uid): _encode_task_uids(subtask_uids)
            for uid, subtask_uids in hierarchy_graph_view.task_subtasks_pairs()
        }

    raise TypeError


def _decode_task_hierarchy_graph(d: dict[str, list[str]]) -> tasks.HierarchyGraph:
    """Decode task hierarchy graph."""
    task_subtasks_map = {
        _decode_task_uid(number): _decode_task_uids(uids) for number, uids in d.items()
    }
    return tasks.HierarchyGraph(
        reduced_dag=graphs.ReducedDAG(
            bidict=graphs.BiDirectionalSetDict(forward=task_subtasks_map)
        )
    )


def _encode_task_dependency_graph(
    dependency_graph_view: tasks.DependencyGraphView,
) -> dict[str, list[str]]:
    """Encode task dependency graph."""
    if isinstance(dependency_graph_view, tasks.DependencyGraphView):
        return {
            _encode_task_uid(uid): _encode_task_uids(dependent_uids)
            for uid, dependent_uids in dependency_graph_view.task_dependents_pairs()
        }

    raise TypeError


def _decode_task_dependency_graph(d: dict[str, list[str]]) -> tasks.DependencyGraph:
    """Decode task dependency graph."""
    task_dependents_map = {
        _decode_task_uid(number): _decode_task_uids(uids) for number, uids in d.items()
    }
    return tasks.DependencyGraph(
        dag=graphs.DirectedAcyclicGraph(
            bidict=graphs.BiDirectionalSetDict(forward=task_dependents_map)
        )
    )


class LocalFileDataLayer(architecture.DataLayer):
    """Local File data layer.

    Implementation of the data-layer interface that stores and retrieves data
    from files on the local filesystem.
    """

    def __init__(self) -> None:
        """Initialise LocalFileDataLayer."""

    @override
    def initialise(self) -> None:
        """Initialise the local file data-layer.

        Creates the necessary directory and files for storing graft data.
        """
        _DATA_DIRECTORY_PATH.mkdir(exist_ok=True)
        with _TASK_HIERARCHY_GRAPH_FILEPATH.open("w") as fp:
            json.dump({}, fp)
        with _TASK_DEPENDENCY_GRAPH_FILEPATH.open("w") as fp:
            json.dump({}, fp)
        with _TASK_ATTRIBUTES_REGISTER_FILEPATH.open("w") as fp:
            json.dump({}, fp)
        _TASK_NEXT_UID_FILEPATH.write_text("0")

    @override
    def get_next_task_uid(self) -> tasks.UID:
        """Return the next task UID."""
        number = int(_TASK_NEXT_UID_FILEPATH.read_text())
        return tasks.UID(number)

    @override
    def increment_next_task_uid_counter(self) -> None:
        number = int(_TASK_NEXT_UID_FILEPATH.read_text())
        number += 1
        _TASK_NEXT_UID_FILEPATH.write_text(str(number))

    @override
    def save_system(self, system: domain.System) -> None:
        """Save the state of the system."""
        _save_task_system(system_view=system.task_system_view())

    @override
    def load_system(self) -> domain.System:
        task_system = _load_task_system()
        return domain.System(task_system=task_system)

    @override
    def load_tasks_attributes_register_view(self) -> tasks.AttributesRegisterView:
        """Return a view of the task attributes register."""
        register = _load_task_attributes_register()
        return tasks.AttributesRegisterView(attributes_register=register)


def _save_task_attributes_register(register: tasks.AttributesRegisterView) -> None:
    """Save the task attributes register."""
    with _TASK_ATTRIBUTES_REGISTER_FILEPATH.open("w") as fp:
        json.dump(obj=register, fp=fp, default=_encode_task_attributes_register)


def _load_task_attributes_register() -> tasks.AttributesRegister:
    """Load the task attributes register."""
    with _TASK_ATTRIBUTES_REGISTER_FILEPATH.open("r") as fp:
        return json.load(fp=fp, object_hook=_decode_task_attributes_register)


def _save_task_hierarchy_graph(graph: tasks.HierarchyGraphView) -> None:
    """Save the task hierarchy graph."""
    with _TASK_HIERARCHY_GRAPH_FILEPATH.open("w") as fp:
        json.dump(obj=graph, fp=fp, default=_encode_task_hierarchy_graph)


def _save_task_dependency_graph(graph: tasks.DependencyGraphView) -> None:
    """Save the task dependency graph."""
    with _TASK_DEPENDENCY_GRAPH_FILEPATH.open("w") as fp:
        json.dump(obj=graph, fp=fp, default=_encode_task_dependency_graph)


def _save_task_system(system_view: tasks.SystemView) -> None:
    """Save the task system."""
    _save_task_attributes_register(register=system_view.attributes_register_view())
    _save_task_hierarchy_graph(graph=system_view.hierarchy_graph_view())
    _save_task_dependency_graph(graph=system_view.dependency_graph_view())


def _load_task_system() -> tasks.System:
    """Load the task system."""
    attributes_register = _load_task_attributes_register()
    hierarchy_graph = _load_task_hierarchy_graph()
    dependency_graph = _load_task_dependency_graph()
    return tasks.System(
        attributes_register=attributes_register,
        hierarchy_graph=hierarchy_graph,
        dependency_graph=dependency_graph,
    )


def _load_task_hierarchy_graph() -> tasks.HierarchyGraph:
    """Load the task hierarchy graph."""
    with _TASK_HIERARCHY_GRAPH_FILEPATH.open("r") as fp:
        return json.load(fp=fp, object_hook=_decode_task_hierarchy_graph)


def _load_task_dependency_graph() -> tasks.DependencyGraph:
    """Load the task dependency graph."""
    with _TASK_DEPENDENCY_GRAPH_FILEPATH.open("r") as fp:
        return json.load(fp=fp, object_hook=_decode_task_dependency_graph)
