from typing import Final


class ArrowStyle:
    def __init__(self, value: str, /) -> None:
        self._value = value

    def __str__(self) -> str:
        return self._value


SIMPLE: Final = ArrowStyle("simple")
CURVE_FILLED_B: Final = ArrowStyle("-|>")
