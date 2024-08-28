from typing import Protocol

from graft.domain import tasks


class EncodeAttributesRegisterFn(Protocol):
    def __call__(self, register: tasks.IAttributesRegisterView) -> str:
        ...


class EncodeHierarchyGraphFn(Protocol):
    def __call__(self, graph: tasks.IHierarchyGraphView) -> str:
        ...


class EncodeDependencyGraphFn(Protocol):
    def __call__(self, graph: tasks.IDependencyGraphView) -> str:
        ...


class EncodeNextUnusedTaskFn(Protocol):
    def __call__(self, task: tasks.UID) -> str:
        ...
