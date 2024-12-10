class ConnectionStyle:
    def __init__(self, value: str, /) -> None:
        self._value = value

    def __str__(self) -> str:
        return self._value


ARC3 = ConnectionStyle("arc3")
