"""Local file data-layer implementation and associated exceptions."""

import datetime as dt
import json
import pathlib
from typing import Final, TypedDict, override

from graft import architecture, domain
from graft.domain import event, task

DATA_DIRECTORY_NAME: Final = "data"

TASK_HIERARCHIES_FILENAME: Final = "task_hierarchies.json"
TASK_DEPENDENCIES_FILENAME: Final = "task_dependencies.json"
TASK_REGISTER_FILENAME: Final = "task_register.json"
TASK_NEXT_ID_FILENAME: Final = "task_next_id.txt"

EVENT_REGISTER_FILENAME: Final = "event_register.json"
EVENT_NEXT_ID_FILENAME: Final = "event_next_id.txt"

DATA_DIRECTORY_PATH = pathlib.Path.cwd() / DATA_DIRECTORY_NAME


TASK_HIERARCHIES_FILEPATH: Final = DATA_DIRECTORY_PATH / TASK_HIERARCHIES_FILENAME
TASK_DEPENDENCIES_FILEPATH: Final = DATA_DIRECTORY_PATH / TASK_DEPENDENCIES_FILENAME
TASK_REGISTER_FILEPATH: Final = DATA_DIRECTORY_PATH / TASK_REGISTER_FILENAME
TASK_NEXT_ID_FILEPATH: Final = DATA_DIRECTORY_PATH / TASK_NEXT_ID_FILENAME

EVENT_REGISTER_FILEPATH: Final = DATA_DIRECTORY_PATH / EVENT_REGISTER_FILENAME
EVENT_NEXT_ID_FILEPATH: Final = DATA_DIRECTORY_PATH / EVENT_NEXT_ID_FILENAME


class TaskAttributesJSONDict(TypedDict):
    name: str | None
    description: str | None
    importance: str | None


class EventAttributesJSONDict(TypedDict):
    name: str | None
    description: str | None
    datetime: str | None


def encode_task_register(o: task.RegisterView) -> dict[str, TaskAttributesJSONDict]:
    """Encode task register."""
    if isinstance(o, task.Register):
        return {
            str(uid): {
                "name": str(attributes.name) if attributes.name is not None else None,
                "description": str(attributes.description)
                if attributes.description is not None
                else None,
                "importance": attributes.importance.value
                if attributes.importance
                else None,
            }
            for uid, attributes in o.items()
        }

    raise TypeError


def decode_task_register(d: dict[str, TaskAttributesJSONDict]) -> task.Register:
    """Decode task register."""
    return task.Register(
        uid_to_attributes_map={
            task.UID(int(uid_str)): task.Attributes(
                name=task.Name(attributes_dict["name"])
                if attributes_dict["name"] is not None
                else None,
                description=task.Description(attributes_dict["description"])
                if attributes_dict["description"] is not None
                else None,
                importance=task.Importance(attributes_dict["importance"])
                if attributes_dict["importance"] is not None
                else None,
            )
            for uid_str, attributes_dict in d.items()
        }
    )


def encode_event_register(o: event.RegisterView) -> dict[str, EventAttributesJSONDict]:
    """Encode event register."""
    if isinstance(o, event.Register):
        return {
            str(uid): {
                "name": str(attributes.name) if attributes.name is not None else None,
                "description": str(attributes.description)
                if attributes.description is not None
                else None,
                "datetime": attributes.datetime.isoformat()
                if attributes.datetime
                else None,
            }
            for uid, attributes in o.items()
        }

    raise TypeError


def decode_event_register(d: dict[str, EventAttributesJSONDict]) -> event.Register:
    """Decode event register."""
    return event.Register(
        uid_to_attributes_map={
            event.UID(int(uid_str)): event.Attributes(
                name=event.Name(attributes_dict["name"])
                if attributes_dict["name"] is not None
                else None,
                description=event.Description(attributes_dict["description"])
                if attributes_dict["description"] is not None
                else None,
                datetime=dt.datetime.fromisoformat(attributes_dict["datetime"])
                if attributes_dict["datetime"] is not None
                else None,
            )
            for uid_str, attributes_dict in d.items()
        }
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
        DATA_DIRECTORY_PATH.mkdir(exist_ok=True)
        with TASK_HIERARCHIES_FILEPATH.open("w") as fp:
            json.dump({}, fp)
        with TASK_DEPENDENCIES_FILEPATH.open("w") as fp:
            json.dump({}, fp)
        with TASK_REGISTER_FILEPATH.open("w") as fp:
            json.dump({}, fp)
        TASK_NEXT_ID_FILEPATH.write_text("0")

        with EVENT_REGISTER_FILEPATH.open("w") as fp:
            json.dump({}, fp)
        EVENT_NEXT_ID_FILEPATH.write_text("0")

    @override
    def get_next_task_uid(self) -> task.UID:
        """Return the next task UID."""
        number = int(TASK_NEXT_ID_FILEPATH.read_text())
        return task.UID(number)

    @override
    def increment_next_task_uid_counter(self) -> None:
        number = int(TASK_NEXT_ID_FILEPATH.read_text())
        number += 1
        TASK_NEXT_ID_FILEPATH.write_text(str(number))

    @override
    def save_system(self, system: domain.System) -> None:
        """Save the state of the system."""
        _save_task_register(register=system.task_register_view)
        _save_event_register(register=system.event_register_view)

        raise NotImplementedError

    @override
    def load_system(self) -> domain.System:
        task_register = _load_task_register()
        event_register = _load_event_register()

        raise NotImplementedError


def _save_task_register(register: task.RegisterView) -> None:
    """Save the task register."""
    with TASK_REGISTER_FILEPATH.open("w") as fp:
        json.dump(obj=register, fp=fp, default=encode_task_register)


def _load_task_register() -> task.Register:
    """Load the task register."""
    with TASK_REGISTER_FILEPATH.open("r") as fp:
        return json.load(fp=fp, object_hook=decode_task_register)


def _save_event_register(register: event.RegisterView) -> None:
    """Save the event register."""
    with EVENT_REGISTER_FILEPATH.open("w") as fp:
        json.dump(obj=register, fp=fp, default=encode_event_register)


def _load_event_register() -> event.Register:
    """Load the event register."""
    with EVENT_REGISTER_FILEPATH.open("r") as fp:
        return json.load(fp=fp, object_hook=decode_event_register)


def _save_task_network(network: task.Network) -> None:
    """Save the task network."""
    raise NotImplementedError
