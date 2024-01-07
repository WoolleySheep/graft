from collections.abc import Callable


class SystemUpdateNotifier:
    def __init__(self) -> None:
        self.update_listeners = list[Callable[[], None]]()

    def add(self, listener: Callable[[], None]) -> None:
        self.update_listeners.append(listener)

    def trigger(self) -> None:
        for listener in self.update_listeners:
            listener()


_singleton = SystemUpdateNotifier()


def get_singleton() -> SystemUpdateNotifier:
    return _singleton
