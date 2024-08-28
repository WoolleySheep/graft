from graft.domain import tasks


def _encode_uid(uid: tasks.UID) -> str:
    """Encode UID."""
    return str(int(uid))


def _decode_uid(number: str) -> tasks.UID:
    """Decode UID."""
    return tasks.UID(int(number))


def encode_next_unused_task(task: tasks.UID) -> str:
    return _encode_uid(task)


def decode_next_unused_task(text: str) -> tasks.UID:
    return _decode_uid(text)
