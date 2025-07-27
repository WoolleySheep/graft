import collections
import itertools
from collections.abc import Callable, Collection, Hashable, Iterable

from graft.graphs.bidict import invert_bidirectional_mapping


class DirectedGraphBuilder[T: Hashable]:
    """Class for building a dictionary representing a directed graph."""

    def __init__(self) -> None:
        self._connections = dict[T, set[T]]()

    def add_node(self, node: T) -> None:
        if node in self._connections:
            return

        self._connections[node] = set[T]()

    def add_edge(self, source: T, target: T) -> None:
        """Add an edge from source to target.

        If source does not exist, create it.
        If target does not exist, create it.
        """
        if source not in self._connections:
            self._connections[source] = set[T]()

        if target not in self._connections:
            self._connections[target] = set[T]()

        self._connections[source].add(target)

    def add_ancestors_subgraph(
        self,
        nodes: Iterable[T],
        get_predecessors: Callable[[T], Collection[T]],
        stop_condition: Callable[[T], bool] | None = None,
    ) -> set[T]:
        """Add an ancestors subgraph."""
        nodes1, nodes2 = itertools.tee(nodes)

        for node in nodes1:
            _ = get_predecessors(node)

        nodes_to_check = collections.deque(nodes2)
        nodes_checked = set[T]()

        for node in nodes_to_check:
            self.add_node(node)

        while nodes_to_check:
            node = nodes_to_check.popleft()
            if node in nodes_checked:
                continue
            nodes_checked.add(node)

            if stop_condition is not None and stop_condition(node):
                continue

            for predecessor in get_predecessors(node):
                self.add_edge(source=predecessor, target=node)
                nodes_to_check.append(predecessor)

        return nodes_checked

    def add_descendants_subgraph(
        self,
        nodes: Iterable[T],
        get_successors: Callable[[T], Collection[T]],
        stop_condition: Callable[[T], bool] | None = None,
    ) -> set[T]:
        """Add a descendants subgraph."""
        nodes1, nodes2 = itertools.tee(nodes)

        for node in nodes1:
            _ = get_successors(node)

        nodes_to_check = collections.deque(nodes2)
        nodes_checked = set[T]()

        for node in nodes_to_check:
            self.add_node(node)

        while nodes_to_check:
            node = nodes_to_check.popleft()
            if node in nodes_checked:
                continue
            nodes_checked.add(node)

            if stop_condition is not None and stop_condition(node):
                continue

            for successor in get_successors(node):
                self.add_edge(source=node, target=successor)
                nodes_to_check.append(successor)

        return nodes_checked

    def add_connecting_subgraph(
        self,
        sources: Iterable[T],
        targets: Iterable[T],
        get_successors: Callable[[T], Collection[T]],
        get_no_connecting_subgraph_exception: Callable[[], Exception],
    ) -> set[T]:
        sources1, sources2 = itertools.tee(sources)
        targets1, targets2 = itertools.tee(targets)

        # Throw an exception if any of the nodes aren't in the graph
        for node in itertools.chain(sources1, targets1):
            _ = get_successors(node)

        source_nodes = list(sources2)
        target_nodes = list(targets2)

        builder = DirectedGraphBuilder[T]()
        _ = builder.add_descendants_subgraph(source_nodes, get_successors)
        node_successors_map = builder.build()
        node_predecessors_map = invert_bidirectional_mapping(node_successors_map)

        for node in target_nodes:
            if node in node_predecessors_map:
                continue

            raise get_no_connecting_subgraph_exception()

        return self.add_ancestors_subgraph(
            target_nodes, lambda node: node_predecessors_map[node]
        )

    def add_component_subgraph(
        self,
        node: T,
        get_successors: Callable[[T], Collection[T]],
        get_predecessors: Callable[[T], Collection[T]],
    ) -> set[T]:
        """Add the component subgraph."""
        _ = get_successors(node)

        nodes_to_check = collections.deque([node])
        nodes_checked = set[T]()

        self.add_node(node)

        while nodes_to_check:
            node = nodes_to_check.popleft()
            if node in nodes_checked:
                continue
            nodes_checked.add(node)

            for predecessor in get_predecessors(node):
                self.add_edge(source=predecessor, target=node)
                nodes_to_check.append(predecessor)

            for successor in get_successors(node):
                self.add_edge(source=node, target=successor)
                nodes_to_check.append(successor)

        return nodes_checked

    def build(self) -> dict[T, set[T]]:
        """Create the dictionary representing the graph."""
        return self._connections
