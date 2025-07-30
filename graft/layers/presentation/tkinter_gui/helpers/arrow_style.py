from typing import Final


class ArrowStyle:
    def __init__(self, value: str, /) -> None:
        self._value = value

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ArrowStyle):
            return NotImplemented

        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(self._value)


SIMPLE: Final = ArrowStyle("simple")
CURVE_FILLED_B: Final = ArrowStyle("-|>")
