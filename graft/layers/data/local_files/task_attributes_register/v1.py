import json
from typing import Any, Final, TypedDict

from graft.domain import tasks

_ENCODED_PROGRESS_NOT_STARTED: Final = "not_started"
_ENCODED_PROGRESS_IN_PROGRESS: Final = "in_progress"
_ENCODED_PROGRESS_COMPLETED: Final = "completed"

_ENCODED_IMPORTANCE_LOW: Final = "final"
_ENCODED_IMPORTANCE_MEDIUM: Final = "medium"
_ENCODED_IMPORTANCE_HIGH: Final = "high"

_NAME_KEY = "name"
_DESCRIPTION_KEY = "description"
_PROGRESS_KEY = "progress"
_IMPORTANCE_KEY = "importance"


class TaskAttributesJSONDict(TypedDict):
    """Dictionary representation of Task Attributes in JSON format."""

    name: str
    description: str
    progress: str | None
    importance: str | None


def _encode_uid(uid: tasks.UID) -> str:
    return str(int(uid))


def _decode_uid(number: str) -> tasks.UID:
    return tasks.UID(int(number))


def _encode_name(name: tasks.Name) -> str:
    return str(name)


def _decode_name(text: str) -> tasks.Name:
    return tasks.Name(text)


def _encode_description(description: tasks.Description) -> str:
    return str(description)


def _decode_description(text: str) -> tasks.Description:
    return tasks.Description(text)


def _encode_progress(progress: tasks.Progress) -> str:
    match progress:
        case tasks.Progress.NOT_STARTED:
            return _ENCODED_PROGRESS_NOT_STARTED
        case tasks.Progress.IN_PROGRESS:
            return _ENCODED_PROGRESS_IN_PROGRESS
        case tasks.Progress.COMPLETED:
            return _ENCODED_PROGRESS_COMPLETED


def _decode_progress(text: str) -> tasks.Progress:
    # TODO: Find a better way to do this than these hideous if statements
    if text == _ENCODED_PROGRESS_NOT_STARTED:
        return tasks.Progress.NOT_STARTED

    if text == _ENCODED_PROGRESS_IN_PROGRESS:
        return tasks.Progress.IN_PROGRESS

    if text == _ENCODED_PROGRESS_COMPLETED:
        return tasks.Progress.COMPLETED

    msg = "Can't decode task progress [{text}]"
    raise ValueError(msg)


def _encode_importance(importance: tasks.Importance) -> str:
    match importance:
        case tasks.Importance.LOW:
            return _ENCODED_IMPORTANCE_LOW
        case tasks.Importance.MEDIUM:
            return _ENCODED_IMPORTANCE_MEDIUM
        case tasks.Importance.HIGH:
            return _ENCODED_IMPORTANCE_HIGH


def _decode_importance(text: str) -> tasks.Importance:
    # TODO: Find a better way to do this than these hideous if statements
    if text == _ENCODED_IMPORTANCE_LOW:
        return tasks.Importance.LOW

    if text == _ENCODED_IMPORTANCE_MEDIUM:
        return tasks.Importance.MEDIUM

    if text == _ENCODED_IMPORTANCE_HIGH:
        return tasks.Importance.HIGH

    msg = f"Can't decode task importance [{text}]"
    raise ValueError(msg)


def _convert_attributes_to_dict(
    attributes: tasks.IAttributesView,
) -> TaskAttributesJSONDict:
    return {
        _NAME_KEY: _encode_name(attributes.name),
        _DESCRIPTION_KEY: _encode_description(attributes.description),
        _PROGRESS_KEY: _encode_progress(attributes.progress)
        if attributes.progress is not None
        else None,
        _IMPORTANCE_KEY: _encode_importance(attributes.importance)
        if attributes.importance is not None
        else None,
    }


def _convert_dict_to_attributes(d: TaskAttributesJSONDict) -> tasks.Attributes:
    return tasks.Attributes(
        name=_decode_name(d[_NAME_KEY]),
        description=_decode_description(d[_DESCRIPTION_KEY]),
        progress=_decode_progress(encoded_progress)
        if (encoded_progress := d[_PROGRESS_KEY]) is not None
        else None,
        importance=(
            _decode_importance(encoded_importance)
            if (encoded_importance := d[_IMPORTANCE_KEY]) is not None
            else None
        ),
    )


def _convert_attributes_register_to_dict(o: Any) -> dict[str, TaskAttributesJSONDict]:
    """Convert attributes register to dict.

    Meant to be used with json.dump.
    """
    # TODO: Improve this hacky function
    if isinstance(o, (tasks.AttributesRegister, tasks.AttributesRegisterView)):
        return {
            _encode_uid(uid): _convert_attributes_to_dict(attributes)
            for uid, attributes in o.items()
        }

    raise TypeError


def _convert_dict_to_attributes_register(
    d: dict[Any, Any],
) -> tasks.AttributesRegister | dict[Any, Any]:
    """Convert dict to attributes register.

    This function will be called on all dictionaries. If it is not the right
    format, return the original dictionary. Meant to be used with json.load.
    """
    # TODO: Improve this hacky function
    try:
        return tasks.AttributesRegister(
            tasks_with_attributes=(
                (_decode_uid(number), _convert_dict_to_attributes(attributes_dict))
                for number, attributes_dict in d.items()
            )
        )
    except ValueError:
        return d


def encode_attributes_register(register: tasks.IAttributesRegisterView) -> str:
    return json.dumps(register, default=_convert_attributes_register_to_dict)


def decode_attributes_register(text: str) -> tasks.AttributesRegister:
    return json.loads(text, object_hook=_convert_dict_to_attributes_register)
