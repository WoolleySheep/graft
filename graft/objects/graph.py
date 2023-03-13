from typing import Any, Hashable, Iterable

import networkx as nx

from graft.objects import task


class NodeDoesNotExistError(Exception):
    def __init__(
        self, node: Hashable, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ):
        self.node = node

        super().__init__(f"node [{node}] does not exist", *args, **kwargs)


class NodeExistsError(Exception):
    def __init__(
        self, node: Hashable, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ):
        self.node = node

        super().__init__(f"node [{node}] already exists", *args, **kwargs)


class EdgeExistsError(Exception):
    def __init__(
        self,
        source: Hashable,
        target: Hashable,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ):
        self.source = source
        self.target = target

        super().__init__(
            f"edge [{source}] -> [{target}] already exists", *args, **kwargs
        )


class EdgeDoesNotExistError(Exception):
    def __init__(
        self,
        source: Hashable,
        target: Hashable,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ):
        self.source = source
        self.target = target

        super().__init__(
            f"edge [{source}] -> [{target}] does not exist", *args, **kwargs
        )


class GraftGraph:
    def __init__(self, digraph: nx.DiGraph | None = None) -> None:
        self._digraph = digraph or nx.DiGraph()

    def has_node(self, node: Hashable) -> bool:
        return self._digraph.has_node(node)

    def add_node(self, node: Hashable) -> None:
        if self.has_node(node):
            raise NodeExistsError(node)

        self._digraph.add_node(node)

    def remove_node(self, node: Hashable) -> None:
        if not self.has_node(node):
            raise NodeDoesNotExistError(node)

        self._digraph.remove_node(node)

    def has_edge(self, source: Hashable, target: Hashable) -> bool:
        for node in (source, target):
            if not self.has_node(node):
                raise NodeDoesNotExistError(node)

        return self._digraph.has_edge(source, target)

    def add_edge(self, source: Hashable, target: Hashable) -> None:
        for node in (source, target):
            if not self.has_node(node):
                raise NodeDoesNotExistError(node)

        if self.has_edge(source, target):
            raise EdgeExistsError(source, target)

        self._digraph.add_edge(source, target)

    def remove_edge(self, source: Hashable, target: Hashable) -> None:
        has_edge = self.has_edge(source, target)

        if not has_edge:
            raise EdgeDoesNotExistError(source, target)

        self._digraph.remove_edge(source, target)

    def descendants(self, node: Hashable) -> set:
        try:
            return nx.descendants(G=self, source=node)
        except nx.NetworkXError as e:
            raise NodeDoesNotExistError(node=node) from e

    def ancestors(self, node: Hashable) -> set:
        try:
            return nx.ancestors(G=self, source=node)
        except nx.NetworkXError as e:
            raise NodeDoesNotExistError(node=node) from e

    def predecessors(self, node: Hashable) -> Iterable[Hashable]:
        try:
            return self._digraph.predecessors(n=node)
        except nx.NetworkXError as e:
            raise NodeDoesNotExistError(node=node) from e

    def successors(self, node: Hashable) -> Iterable[Hashable]:
        try:
            return self._digraph.successors(node)
        except nx.NetworkXError as e:
            raise NodeDoesNotExistError(node=node) from e


class ConstrainedGraph(GraftGraph):
    pass


class TaskHierarchies(ConstrainedGraph):
    def has_task(self, id: task.Id) -> None:
        return super().has_node(id)

    def add_task(self, id: task.Id) -> None:
        return super().add_node(id)

    def remove_task(self, id: task.Id) -> None:
        return super().remove_node(id)

    def has_hierarchy(self, parent_id: task.Id, child_id: task.Id) -> None:
        return super().has_edge(parent_id, child_id)

    def add_hierarchy(self, parent_id: task.Id, child_id: task.Id) -> None:
        return super().add_edge(parent_id, child_id)

    def remove_hierarchy(welf, parent_id: task.Id, child_id: task.Id) -> None:
        return super().remove_edge(parent_id, child_id)

    def parents(self, id: task.Id) -> Iterable[task.Id]:
        return super().predecessors(id)

    def children(self, id: task.Id) -> Iterable[task.Id]:
        return super().successors(id)

    def ancestors(self, id: task.Id) -> set[task.Id]:
        return super().ancestors(id)

    def descendants(self, id: task.Id) -> set[task.Id]:
        return super().descendants(id)
