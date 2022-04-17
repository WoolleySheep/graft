import enum

_NOT_STARTED = "not started"
_IN_PROGRESS = "in progress"

_PROGRESS_INDEX_MAP = {_NOT_STARTED: 0, _IN_PROGRESS: 1}


class Progress(enum.Enum):
    NOT_STARTED = _NOT_STARTED
    IN_PROGRESS = _IN_PROGRESS
    COMPLETED = "completed"

    def __lt__(self, other: "Progress") -> bool:
        if self.__class__ is not other.__class__:
            raise NotImplementedError
        # Will raise KeyError if comparing against completed (deliberate)
        return _PROGRESS_INDEX_MAP[self.value] < _PROGRESS_INDEX_MAP[other.value]

    def __gt__(self, other: "Progress") -> bool:
        if self.__class__ is not other.__class__:
            raise NotImplementedError
        # Will raise KeyError if comparing against completed (deliberate)
        return _PROGRESS_INDEX_MAP[self.value] > _PROGRESS_INDEX_MAP[other.value]
