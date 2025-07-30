from typing import Final


class LineStyle:
    def __init__(self, value: str, /) -> None:
        self._value = value

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LineStyle):
            return NotImplemented

        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(self._value)


SOLID: Final = LineStyle("solid")
DASHED: Final = LineStyle("dashed")
DASHED_DOTTED: Final = LineStyle("dashdot")
DOTTED: Final = LineStyle("dotted")
