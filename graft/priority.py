import enum

_OPTIONAL = "optional"
_LOW = "low"
_MEDIUM = "medium"
_HIGH = "high"
_CRITICAL = "critical"

_PRIORITY_INDEX_MAP = {
    _OPTIONAL: 0,
    _LOW: 1,
    _MEDIUM: 2,
    _HIGH: 3,
    _CRITICAL: 4,
}


class Priority(enum.Enum):
    OPTIONAL = _OPTIONAL
    LOW = _LOW
    MEDIUM = _MEDIUM
    HIGH = _HIGH
    CRITICAL = _CRITICAL

    def __lt__(self, other: "Priority") -> bool:
        if self.__class__ is not other.__class__:
            raise NotImplementedError
        return _PRIORITY_INDEX_MAP[self.value] < _PRIORITY_INDEX_MAP[other.value]

    def __gt__(self, other: "Priority") -> bool:
        if self.__class__ is not other.__class__:
            raise NotImplementedError
        return _PRIORITY_INDEX_MAP[self.value] > _PRIORITY_INDEX_MAP[other.value]
