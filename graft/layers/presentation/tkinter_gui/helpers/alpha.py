from typing import Final


class Alpha:
    def __init__(self, value: float, /) -> None:
        if not (0 <= value <= 1):
            msg = "Alpha must be in range [0, 1]."
            raise ValueError(msg)

        self._value = value

    def __float__(self) -> float:
        return float(self._value)


OPAQUE: Final = Alpha(1)
TRANSPARENT: Final = Alpha(0)
