"""Local file data-layer implementation and associated exceptions."""

import json
import pathlib
from typing import Final, TypedDict, override

from graft import architecture, domain
from graft.domain import task

DATA_DIRECTORY_NAME: Final = "data"

TASK_HIERARCHY_GRAPH_FILENAME: Final = "task_hierarchy_graph.json"
TASK_DEPENDENCY_GRAPH_FILENAME: Final = "task_dependencies.json"
TASK_ATTRIBUTES_REGISTER_FILENAME: Final = "task_attributes_register.json"
TASK_NEXT_UID_FILENAME: Final = "task_next_uid.txt"

DATA_DIRECTORY_PATH = pathlib.Path.cwd() / DATA_DIRECTORY_NAME

TASK_HIERARCHY_GRAPH_FILEPATH: Final = (
    DATA_DIRECTORY_PATH / TASK_HIERARCHY_GRAPH_FILENAME
)
TASK_DEPENDENCY_GRAPH_FILEPATH: Final = (
    DATA_DIRECTORY_PATH / TASK_DEPENDENCY_GRAPH_FILENAME
)
TASK_ATTRIBUTES_REGISTER_FILEPATH: Final = (
    DATA_DIRECTORY_PATH / TASK_ATTRIBUTES_REGISTER_FILENAME
)
TASK_NEXT_UID_FILEPATH: Final = DATA_DIRECTORY_PATH / TASK_NEXT_UID_FILENAME


class TaskAttributesJSONDict(TypedDict):
    name: str | None
    description: str | None


def _encode_task_uid(uid: task.UID) -> str:
    """Encode task UID."""
    return str(uid)


def _decode_task_uid(number: str) -> task.UID:
    """Decode task UID."""
    return task.UID(int(number))


def _encode_task_attributes_register(
    o: task.AttributesRegisterView,
) -> dict[str, TaskAttributesJSONDict]:
    """Encode task attributes register."""

    def encode_attributes(attributes: task.AttributesView) -> TaskAttributesJSONDict:
        return {
            "name": str(attributes.name) if attributes.name is not None else None,
            "description": str(attributes.description)
            if attributes.description is not None
            else None,
        }

    if isinstance(o, task.AttributesRegister):
        return {
            _encode_task_uid(uid): encode_attributes(attributes)
            for uid, attributes in o.items()
        }

    raise TypeError


def _decode_task_attributes_register(
    d: dict[str, TaskAttributesJSONDict],
) -> task.AttributesRegister:
    """Decode task register."""

    def decode_attributes(d: TaskAttributesJSONDict) -> task.Attributes:
        return task.Attributes(
            name=task.Name(d["name"]) if d["name"] is not None else None,
            description=(
                task.Description(d["description"])
                if d["description"] is not None
                else None
            ),
        )

    return task.AttributesRegister(
        uid_to_attributes_map={
            _decode_task_uid(number): decode_attributes(attributes_dict)
            for number, attributes_dict in d.items()
        }
    )


def _encode_task_hierarchy_graph(hierarchy_graph_view: task.HierarchyGraphView) -> dict[str, list[str]]:
    """Encode task hierarchy graph."""
    def encode_uids(uids: task.UIDsView) -> list[str]:
        return [_encode_task_uid(uid) for uid in uids]


    if isinstance(hierarchy_graph_view, task.HierarchyGraphView):
        return {
            _encode_task_uid(uid): encode_uids(subtask_uids)
            for uid, subtask_uids in hierarchy_graph_view.task_subtasks_pairs()
        }

    raise TypeError

def _decode_task_hierarchy_graph(d: dict[str, list[str]]) -> task.HierarchyGraph:
    """Decode task hierarchy graph."""
    raise NotImplementedError



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
        DATA_DIRECTORY_PATH.mkdir(exist_ok=True)
        with TASK_HIERARCHY_GRAPH_FILEPATH.open("w") as fp:
            json.dump({}, fp)
        with TASK_DEPENDENCY_GRAPH_FILEPATH.open("w") as fp:
            json.dump({}, fp)
        with TASK_ATTRIBUTES_REGISTER_FILEPATH.open("w") as fp:
            json.dump({}, fp)
        TASK_NEXT_UID_FILEPATH.write_text("0")

    @override
    def get_next_task_uid(self) -> task.UID:
        """Return the next task UID."""
        number = int(TASK_NEXT_UID_FILEPATH.read_text())
        return task.UID(number)

    @override
    def increment_next_task_uid_counter(self) -> None:
        number = int(TASK_NEXT_UID_FILEPATH.read_text())
        number += 1
        TASK_NEXT_UID_FILEPATH.write_text(str(number))

    @override
    def save_system(self, system: domain.System) -> None:
        """Save the state of the system."""
        _save_task_system(system_view=system.task_system_view())

    @override
    def load_system(self) -> domain.System:
        task_system = _load_task_system()
        return domain.System(task_system=task_system)


def _save_task_attributes_register(register: task.AttributesRegisterView) -> None:
    """Save the task attributes register."""
    with TASK_ATTRIBUTES_REGISTER_FILEPATH.open("w") as fp:
        json.dump(obj=register, fp=fp, default=_encode_task_attributes_register)


def _load_task_attributes_register() -> task.AttributesRegister:
    """Load the task attributes register."""
    with TASK_ATTRIBUTES_REGISTER_FILEPATH.open("r") as fp:
        return json.load(fp=fp, object_hook=_decode_task_attributes_register)


def _save_task_hierarchy_graph(graph: task.HierarchyGraphView) -> None:
    """Save the task hierarchy graph."""
    raise NotImplementedError


def _save_task_dependency_graph(graph: task.DependencyGraphView) -> None:
    """Save the task dependency graph."""
    raise NotImplementedError


def _save_task_system(system_view: task.SystemView) -> None:
    """Save the task system."""
    _save_task_attributes_register(register=system_view.attributes_register_view())
    _save_task_hierarchy_graph(graph=system_view.hierarchy_graph_view())
    _save_task_dependency_graph(graph=system_view.dependency_graph_view())


def _load_task_system() -> task.System:
    """Load the task system."""
    attributes_register = _load_task_attributes_register()
    hierarchy_graph = _load_task_hierarchy_graph()
    dependency_graph = _load_task_dependency_graph()
    return task.System(
        attributes_register=attributes_register,
        hierarchy_graph=hierarchy_graph,
        dependency_graph=dependency_graph,
    )


def _load_task_hierarchy_graph() -> task.HierarchyGraph:
    """Load the task hierarchy graph."""
    raise NotImplementedError


def _load_task_dependency_graph() -> task.DependencyGraph:
    """Load the task dependency graph."""
    raise NotImplementedError
