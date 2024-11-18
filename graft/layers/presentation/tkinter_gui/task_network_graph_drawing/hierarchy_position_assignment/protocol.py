from typing import Protocol

from graft.domain import tasks


class GetHierarchyPositions(Protocol):
    def __call__(self, graph: tasks.INetworkGraphView) -> dict[tasks.UID, int]:
        ...
