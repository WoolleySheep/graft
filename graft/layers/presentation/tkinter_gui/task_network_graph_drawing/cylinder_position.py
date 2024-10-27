class TaskCylinderPosition:
    def __init__(
        self,
        min_dependency_position: float,
        max_dependency_position: float,
        hierarchy_position: float,
        depth_position: float,
    ) -> None:
        if min_dependency_position > max_dependency_position:
            msg = "Min dependency position must be <= max dependency position"
            raise ValueError(
                msg
            )

        self._min_dependency = min_dependency_position
        self._max_dependency = max_dependency_position
        self._hierarchy = hierarchy_position
        self._depth = depth_position

    @property
    def min_dependency(self) -> float:
        return self._min_dependency

    @property
    def max_dependency(self) -> float:
        return self._max_dependency

    @property
    def hierarchy(self) -> float:
        return self._hierarchy

    @property
    def depth(self) -> float:
        return self._depth
