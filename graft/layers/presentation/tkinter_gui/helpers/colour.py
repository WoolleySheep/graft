from typing import Final


class Colour:
    """Represents a matplotlib colour.

    No validation applied at this stage, because matplotlib accepts just about anything.
    """

    def __init__(self, value: str, /) -> None:
        self._value = value

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Colour):
            return NotImplemented

        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(self._value)


RED: Final = Colour("red")
GREEN: Final = Colour("green")
BLUE: Final = Colour("blue")
YELLOW: Final = Colour("yellow")
ORANGE: Final = Colour("orange")
PURPLE: Final = Colour("purple")
BLACK: Final = Colour("black")
CYAN: Final = Colour("cyan")
WHITE: Final = Colour("white")
GREY: Final = Colour("grey")
LIGHT_YELLOW: Final = Colour("lightyellow")
LIGHT_BLUE: Final = Colour("lightblue")
