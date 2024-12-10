from typing import Final


class Colour:
    """Represents a matplotlib colour.

    No validation applied at this stage, because matplotlib accepts just about anything.
    """

    def __init__(self, value: str, /) -> None:
        self._value = value

    def __str__(self) -> str:
        return self._value


RED: Final = Colour("red")
GREEN: Final = Colour("green")
BLUE: Final = Colour("blue")
YELLOW: Final = Colour("yellow")
ORANGE: Final = Colour("orange")
PURPLE: Final = Colour("purple")
BLACK: Final = Colour("black")
CYAN: Final = Colour("cyan")
