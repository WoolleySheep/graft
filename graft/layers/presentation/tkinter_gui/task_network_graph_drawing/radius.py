class Radius:
    """The radius of a dimensionless circle."""

    def __init__(self, value: float, /) -> None:
        if value < 0:
            msg = "Radius cannot be negative."
            raise ValueError(msg)

        self._value = value

    def __float__(self) -> float:
        return self._value
