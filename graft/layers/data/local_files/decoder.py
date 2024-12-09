from typing import Protocol

from graft.domain import tasks


class DecodeAttributesRegisterFn(Protocol):
    def __call__(self, text: str) -> tasks.AttributesRegister: ...


class DecodeHierarchyGraphFn(Protocol):
    def __call__(self, text: str) -> tasks.HierarchyGraph: ...


class DecodeDependencyGraphFn(Protocol):
    def __call__(self, text: str) -> tasks.DependencyGraph: ...


class DecodeNextUnusedTaskFn(Protocol):
    def __call__(self, text: str) -> tasks.UID: ...
