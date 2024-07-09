"""Local file data-layer implementation and associated exceptions."""

import enum
import json
import pathlib
import shutil
from collections.abc import Callable, Generator, Iterable
from typing import Any, Final, TypedDict, override

from graft import architecture, domain, graphs
from graft.domain import tasks
from graft.domain.tasks.system import SystemView

_STARTING_TASK_ID_NUMBER = 0

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


class PartiallyInitialisedError(Exception):
    """Exception raised when a data-layer is partially initialised."""


class TaskAttributesJSONDict(TypedDict):
    """Dictionary representation of Task Attributes in JSON format."""

    name: str
    description: str
    progress: str | None
    importance: str | None


def _encode_task_uid(uid: tasks.UID) -> str:
    """Encode task UID."""
    return str(uid)


def _decode_task_uid(number: str) -> tasks.UID:
    """Decode task UID."""
    return tasks.UID(int(number))


def _encode_task_attributes_register(
    o: Any,
) -> dict[str, TaskAttributesJSONDict]:
    """Encode task attributes register."""

    def encode_attributes(attributes: tasks.AttributesView) -> TaskAttributesJSONDict:
        return {
            "name": str(attributes.name),
            "description": str(attributes.description),
            "progress": attributes.progress.value
            if attributes.progress is not None
            else None,
            "importance": attributes.importance.value
            if attributes.importance is not None
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
        if (
            "name" not in d
            or "description" not in d
            or "progress" not in d
            or "importance" not in d
        ):
            raise ValueError  # TODO (mjw): Use better named error

        return tasks.Attributes(
            name=tasks.Name(d["name"]),
            description=(tasks.Description(d["description"])),
            progress=(
                tasks.Progress(d["progress"]) if d["progress"] is not None else None
            ),
            importance=(
                tasks.Importance(d["importance"])
                if d["importance"] is not None
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


def _encode_relationships[T](
    relationships: Iterable[tuple[T, Iterable[T]]], encode: Callable[[T], str]
) -> dict[str, list[str]]:
    return {
        encode(key): [encode(value) for value in values]
        for (key, values) in relationships
    }


def _decode_relationships[T](
    d: dict[str, list[str]], decode: Callable[[str], T]
) -> Generator[tuple[T, Generator[T, None, None]], None, None]:
    for key, values in d.items():
        yield decode(key), (decode(value) for value in values)


def _encode_task_relationships(
    relationships: Iterable[tuple[tasks.UID, Iterable[tasks.UID]]],
) -> dict[str, list[str]]:
    """Encode relationships between task UIDs."""
    return _encode_relationships(relationships, _encode_task_uid)


def _decode_task_relationships(
    d: dict[str, list[str]],
) -> Generator[tuple[tasks.UID, Generator[tasks.UID, None, None]], None, None]:
    """Decode relationships between task UIDs."""
    return _decode_relationships(d, _decode_task_uid)


class InitialisationStatus(enum.Enum):
    """Initialisation status of the local filesystem."""

    NOT_INITIALISED = "not initialised"
    PARTIALLY_INITIALISED = "partially initialised"
    FULLY_INITIALISED = "fully initialised"


class LocalFileDataLayer(architecture.DataLayer):
    """Local File data layer.

        Implementation of the data-layer interface that stores and retrieves data
        from files on the local filesystem.
    import shutil
    """

    def __init__(self) -> None:
        """Initialise LocalFileDataLayer.

        If the filesystem has not been initialised, will do so automatically.
        """

        def get_initialisation_status() -> InitialisationStatus:
            """Get the initialisation status of the local filesystem."""
            if not _DATA_DIRECTORY_PATH.exists():
                return InitialisationStatus.NOT_INITIALISED

            return (
                InitialisationStatus.FULLY_INITIALISED
                if (
                    _TASK_HIERARCHY_GRAPH_FILEPATH.exists()
                    and _TASK_DEPENDENCY_GRAPH_FILEPATH.exists()
                    and _TASK_ATTRIBUTES_REGISTER_FILEPATH.exists()
                    and _TASK_NEXT_UID_FILEPATH.exists()
                )
                else InitialisationStatus.PARTIALLY_INITIALISED
            )

        match get_initialisation_status():
            case InitialisationStatus.NOT_INITIALISED:
                self._initialise()
            case InitialisationStatus.PARTIALLY_INITIALISED:
                raise PartiallyInitialisedError
            case InitialisationStatus.FULLY_INITIALISED:
                pass

    @override
    def erase(self) -> None:
        """Erase all data."""
        shutil.rmtree(_DATA_DIRECTORY_PATH)
        self._initialise()

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

    def _initialise(self) -> None:
        """Initialise the local file data-layer."""
        _DATA_DIRECTORY_PATH.mkdir()
        _save_task_system(system_view=SystemView(system=tasks.System.empty()))
        _TASK_NEXT_UID_FILEPATH.write_text(str(_STARTING_TASK_ID_NUMBER))


def _save_task_attributes_register(register: tasks.AttributesRegisterView) -> None:
    """Save the task attributes register."""
    with _TASK_ATTRIBUTES_REGISTER_FILEPATH.open("w") as fp:
        json.dump(obj=register, fp=fp, default=_encode_task_attributes_register)


def _load_task_attributes_register() -> tasks.AttributesRegister:
    """Load the task attributes register."""
    with _TASK_ATTRIBUTES_REGISTER_FILEPATH.open("r") as fp:
        return json.load(fp=fp, object_hook=_decode_task_attributes_register)


def _save_task_hierarchy_graph(graph: tasks.IHierarchyGraphView) -> None:
    """Save the task hierarchy graph."""
    with _TASK_HIERARCHY_GRAPH_FILEPATH.open("w") as fp:
        json.dump(
            obj=graph.task_subtasks_pairs(), fp=fp, default=_encode_task_relationships
        )


def _save_task_dependency_graph(graph: tasks.IDependencyGraphView) -> None:
    """Save the task dependency graph."""
    with _TASK_DEPENDENCY_GRAPH_FILEPATH.open("w") as fp:
        json.dump(
            obj=graph.task_dependents_pairs(), fp=fp, default=_encode_task_relationships
        )


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
        hierarchy_relationships = json.load(
            fp=fp, object_hook=_decode_task_relationships
        )
    return tasks.HierarchyGraph(
        reduced_dag=graphs.ReducedDAG(
            bidict=graphs.BiDirectionalSetDict(forward=hierarchy_relationships)
        )
    )


def _load_task_dependency_graph() -> tasks.DependencyGraph:
    """Load the task dependency graph."""
    with _TASK_DEPENDENCY_GRAPH_FILEPATH.open("r") as fp:
        dependency_relationships = json.load(
            fp=fp, object_hook=_decode_task_relationships
        )
    return tasks.DependencyGraph(
        dag=graphs.DirectedAcyclicGraph(
            bidict=graphs.BiDirectionalSetDict(forward=dependency_relationships)
        )
    )
