import enum

_LESS_THAN_1_HOUR = "< 1 hour"
_LESS_THAN_1_DAY = "< 1 day"
_LESS_THAN_1_WEEK = "< 1 week"
_LESS_THAN_1_MONTH = "< 1 month"
_LESS_THAN_1_YEAR = "< 1 year"
_ONGOING = "ongoing"

_DURATION_INDEX_MAP = {
    _LESS_THAN_1_HOUR: 0,
    _LESS_THAN_1_DAY: 1,
    _LESS_THAN_1_WEEK: 2,
    _LESS_THAN_1_MONTH: 3,
    _LESS_THAN_1_YEAR: 4,
    _ONGOING: 5,
}


class Duration(enum.Enum):
    LESS_THAN_1_HOUR = _LESS_THAN_1_HOUR
    LESS_THAN_1_DAY = _LESS_THAN_1_DAY
    LESS_THAN_1_WEEK = _LESS_THAN_1_WEEK
    LESS_THAN_1_MONTH = _LESS_THAN_1_MONTH
    LESS_THAN_1_YEAR = _LESS_THAN_1_YEAR
    ONGOING = _ONGOING

    def __lt__(self, other: "Duration") -> bool:
        if self.__class__ is not other.__class__:
            raise NotImplementedError
        return _DURATION_INDEX_MAP[self.value] < _DURATION_INDEX_MAP[other.value]

    def __gt__(self, other: "Duration") -> bool:
        if self.__class__ is not other.__class__:
            raise NotImplementedError
        return _DURATION_INDEX_MAP[self.value] > _DURATION_INDEX_MAP[other.value]
