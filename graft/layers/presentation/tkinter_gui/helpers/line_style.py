from typing import Final


class LineStyle:
    def __init__(self, value: str, /) -> None:
        self._value = value

    def __str__(self) -> str:
        return self._value


SOLID: Final = LineStyle("solid")
DASHED: Final = LineStyle("dashed")
DASHED_DOTTED: Final = LineStyle("dashdot")
DOTTED: Final = LineStyle("dotted")
