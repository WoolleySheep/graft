class DependencyPosition:
    """Class to represent the position of a task cylinder in the dependency axis."""

    def __init__(self, min_: int, max_: int) -> None:
        if min_ > max_:
            msg = "min must be less than or equal to max"
            raise ValueError(msg)

        self._min = min_
        self._max = max_

    @property
    def min(self) -> int:
        return self._min

    @property
    def max(self) -> int:
        return self._max
