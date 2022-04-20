import itertools
import json
from collections import deque
from typing import Hashable, Iterable

import networkx as nx


class NodeExistsError(Exception):
    def __init__(self, node: Hashable, *args, **kwargs):
        self.node = node

        super().__init__(f"node [{node}] already exists", *args, **kwargs)


class NodeDoesNotExistError(Exception):
    def __init__(self, node: Hashable, *args, **kwargs):
        self.node = node

        super().__init__(f"node [{node}] does not exist", *args, **kwargs)


class SelfLoopError(Exception):
    def __init__(self, node: Hashable, *args, **kwargs):
        self.node = node

        super().__init__("No self loops allowed", *args, **kwargs)


class EdgeIntroducesCycleError(Exception):
    def __init__(
        self,
        source: Hashable,
        target: Hashable,
        network: "ConstrainedGraph",
        *args,
        **kwargs,
    ):
        self.source = source
        self.target = target
        # TODO: Save the cyclical section of the DiGraph, not the paths
        #   - G.subgraph.copy() is your friend here
        # Assumption that adding the edge DOES introduce a cycle
        # Hence there must exist 1 or more paths from target to source
        self.paths = []
        for partial_path in nx.all_simple_paths(
            G=network, source=target, target=source
        ):
            full_path = [source] + partial_path
            self.paths.append(full_path)

        formatted_paths = []
        for path in sorted(self.paths):
            formatted_nodes = (f"[{node}]" for node in path)
            formatted_path = " -> ".join(formatted_nodes)
            formatted_paths.append(formatted_path)
        paths_formatted = ", ".join(formatted_paths)

        super().__init__(
            f"edge [{source}] -> [{target}] introduces a cycle into the graph, paths: {paths_formatted}",
            *args,
            **kwargs,
        )


class EdgeExistsError(Exception):
    def __init__(self, source: Hashable, target: Hashable, *args, **kwargs):
        self.source = source
        self.target = target

        super().__init__(
            f"edge [{source}] -> [{target}] already exists", *args, **kwargs
        )


class EdgeDoesNotExistError(Exception):
    def __init__(self, source: Hashable, target: Hashable, *args, **kwargs):
        self.source = source
        self.target = target

        super().__init__(
            f"edge [{source}] -> [{target}] does not exist", *args, **kwargs
        )


class DescendantError(Exception):
    def __init__(
        self,
        source: Hashable,
        target: Hashable,
        network: "ConstrainedGraph",
        *args,
        **kwargs,
    ):
        self.source = source
        self.target = target
        # TODO: Save the offending section of the DiGraph, not the paths
        self.paths = list(nx.all_simple_paths(G=network, source=source, target=target))

        formatted_paths = []
        for path in sorted(self.paths):
            formatted_nodes = (f"[{node}]" for node in path)
            formatted_path = " -> ".join(formatted_nodes)
            formatted_paths.append(formatted_path)
        paths_formatted = ", ".join(formatted_paths)

        super().__init__(
            f"node [{target}] is a descendant of [{source}], paths: {paths_formatted}",
            *args,
            **kwargs,
        )


class PredecessorsError(Exception):
    def __init__(self, node: Hashable, graph: "ConstrainedGraph", *args, **kwargs):
        self.node = node
        self.predecessors = set(graph.predecessors(node))

        formatted_predecessors = ", ".join(
            f"[{node}]" for node in sorted(self.predecessors)
        )

        super().__init__(
            f"node [{node}] has predecessors: {formatted_predecessors}", *args, **kwargs
        )


class SuccessorsError(Exception):
    def __init__(self, node: Hashable, graph: "ConstrainedGraph", *args, **kwargs):
        self.node = node
        self.successors = set(graph.successors(node))

        formatted_successors = ", ".join(
            f"[{node}]" for node in sorted(self.successors)
        )

        super().__init__(
            f"node [{node}] has successors: {formatted_successors}", *args, **kwargs
        )


class SuccessorOfAncestorError(Exception):
    def __init__(
        self,
        source: Hashable,
        target: Hashable,
        network: "ConstrainedGraph",
        *args,
        **kwargs,
    ):
        self.source = source
        self.target = target
        # TODO: Save the offending section of the DiGraph

        self.ancestors = set()
        nodes_to_search = deque(network.predecessors(source))
        searched_nodes = set()
        while nodes_to_search:
            node = nodes_to_search.popleft()
            searched_nodes.add(node)

            if network.has_edge(node, target):
                self.ancestors.add(node)
                # There can be no more target predecessors among this node's ancestors
                searched_nodes.update(network.ancestors(node))
                continue

            predecessors = network.predecessors(node)
            unsearched_predecessors = (
                node for node in predecessors if node not in searched_nodes
            )
            nodes_to_search.extend(unsearched_predecessors)

        formatted_ancestors = (f"[{node}]" for node in sorted(self.ancestors))
        ancestors_formatted = ", ".join(formatted_ancestors)

        super().__init__(
            f"node [{target}] is a successor of [{source}]'s ancestors: {ancestors_formatted}",
            *args,
            **kwargs,
        )


class ConstrainedGraph(nx.DiGraph):
    def __init__(self, mimic: bool = True, *args, **kwargs):
        self.mimic = mimic
        super().__init__(*args, **kwargs)

    def add_node(self, node: Hashable) -> None:
        if not self.mimic and node in self:
            raise NodeExistsError(node=node)
        super().add_node(node)

    def remove_node(self, node: Hashable) -> None:
        if not self.mimic and self.has_predecessors(node=node):
            raise PredecessorsError(node=node, graph=self)

        if not self.mimic and self.has_successors(node=node):
            raise SuccessorsError(node=node, graph=self)

        try:
            super().remove_node(node)
        except nx.NetworkXError as e:
            raise NodeDoesNotExistError(node=node) from e

    def has_predecessors(self, node: Hashable) -> bool:
        try:
            predecessors = self.predecessors(node=node)
        except nx.NetworkXError as e:
            raise NodeDoesNotExistError(node=node) from e

        return bool(list(predecessors))

    def has_successors(self, node: Hashable) -> bool:
        try:
            successors = self.successors(node=node)
        except nx.NetworkXError as e:
            raise NodeDoesNotExistError(node=node) from e

        return bool(list(successors))

    def remove_node_and_links(self, node: Hashable) -> None:
        try:
            super().remove_node(node)
        except nx.NetworkXError as e:
            raise NodeDoesNotExistError(node=node) from e

    def remove_node_and_relink(self, node: Hashable) -> None:
        predecessors = self.predecessors(node=node)
        successors = self.successors(node=node)
        for predecessor, successor in itertools.product(predecessors, successors):
            super().add_edge(predecessor, successor)
        super().remove_node(node)

    def has_edge(self, source: Hashable, target: Hashable) -> bool:
        return super().has_edge(source, target)

    def add_edge(self, source: Hashable, target: Hashable) -> None:
        for node in (source, target):
            if node not in self:
                raise NodeDoesNotExistError(node=node)

        if source == target:
            raise SelfLoopError(node=node)

        if not self.mimic and super().has_edge(source, target):
            raise EdgeExistsError(source=source, target=target)

        if self._is_descentant(source=source, target=target):
            raise DescendantError(source=source, target=target, network=self)

        if self._is_successor_of_ancestor(source=source, target=target):
            raise SuccessorOfAncestorError(source=source, target=target, network=self)

        if self._adding_edge_introduces_cycle(source=source, target=target):
            raise EdgeIntroducesCycleError(source=source, target=target, network=self)

        super().add_edge(source, target)

    def remove_edge(self, source: Hashable, target: Hashable) -> None:
        for node in (source, target):
            if node not in self:
                raise NodeDoesNotExistError(node=node)

        if source == target:
            raise SelfLoopError(node=node)

        try:
            super().remove_edge(source, target)
        except nx.NetworkXError as e:
            raise EdgeDoesNotExistError(source=source, target=target) from e

    def _is_descentant(self, source: Hashable, target: Hashable) -> bool:
        nodes_to_search = deque(self.successors(source))
        searched_nodes = set()
        while nodes_to_search:
            node = nodes_to_search.popleft()
            if node == target:
                return True
            searched_nodes.add(node)
            successors = self.successors(node)
            unsearched_successors = (
                node for node in successors if node not in searched_nodes
            )
            nodes_to_search.extend(unsearched_successors)

        return False

    def _is_successor_of_ancestor(self, source: Hashable, target: Hashable) -> bool:
        nodes_to_search = deque(self.predecessors(source))
        searched_nodes = set()
        while nodes_to_search:
            node = nodes_to_search.popleft()
            if self.has_edge(node, target):
                return True
            searched_nodes.add(node)
            predecessors = self.predecessors(node)
            unsearched_predecessors = (
                node for node in predecessors if node not in searched_nodes
            )
            nodes_to_search.extend(unsearched_predecessors)

        return False

    def _adding_edge_introduces_cycle(self, source: Hashable, target: Hashable) -> bool:
        """Check if adding an edge between source and target introduces a cycle into the graph."""
        checked_nodes = set()
        nodes_to_check = set((target,))
        while nodes_to_check:
            node = nodes_to_check.pop()
            for successor in self.successors(node):
                if successor == source:
                    return True
                if successor not in checked_nodes and successor not in nodes_to_check:
                    nodes_to_check.add(successor)

            checked_nodes.add(node)

        return False

    def has_cycle(self) -> bool:
        try:
            nx.find_cycle(self)
        except nx.NetworkXNoCycle:
            return False
        else:
            return True

    def relabel_node(self, old_label: Hashable, new_label: Hashable) -> None:
        if old_label not in self:
            raise NodeDoesNotExistError(node=old_label)
        if new_label in self:
            raise NodeExistsError(node=new_label)

        nx.relabel_nodes(self, {old_label: new_label}, copy=False)

    def descendents(self, node: Hashable) -> set:
        return nx.descendants(G=self, source=node)

    def ancestors(self, node: Hashable) -> set:
        return nx.ancestors(G=self, source=node)

    def predecessors(self, node: Hashable) -> Iterable[Hashable]:
        try:
            return super().predecessors(node)
        except nx.NetworkXError as e:
            raise NodeDoesNotExistError(node=node) from e

    def successors(self, node: Hashable) -> Iterable[Hashable]:
        try:
            return super().successors(node)
        except nx.NetworkXError as e:
            raise NodeDoesNotExistError(node=node) from e

    def root_nodes(self) -> Iterable[Hashable]:
        return (node for node, predecessors in self.pred.items() if not predecessors)

    def leaf_nodes(self) -> Iterable[Hashable]:
        return (node for node, successors in self.succ.items() if not successors)

    def is_leaf_node(self, node: Hashable) -> bool:
        return not self.succ[node]

    def is_root_node(self, node: Hashable) -> bool:
        return not self.pred[node]


def is_node_valid(node: Hashable) -> bool:
    """Check that a node name can be saved without causing problems"""
    return "," not in json.dumps(node)
