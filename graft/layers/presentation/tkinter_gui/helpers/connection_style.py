from typing import Final


class ConnectionStyle:
    def __init__(self, value: str, /) -> None:
        self._value = value

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ConnectionStyle):
            return NotImplemented

        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(self._value)


ARC3: Final = ConnectionStyle("arc3")
ARC3RAD2: Final = ConnectionStyle("arc3,rad=0.2")
