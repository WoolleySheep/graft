import itertools
import json
from collections import deque
from typing import Hashable, Iterable

import networkx as nx

from graft.acyclic_digraph import (
    AcyclicDiGraph,
    EdgeExistsError,
    EdgeIntroducesCycleError,
    NodeDoesNotExistError,
    NodeExistsError,
    SelfLoopError,
)


class HasPathError(Exception):
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

        # TODO: Update error message
        super().__init__(
            f"node [{target}] is a descendant of [{source}], paths: {paths_formatted}",
            *args,
            **kwargs,
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


class NoTargetPredecessorsAsSourceAncestorsError(Exception):
    def __init__(self, source: Hashable, target: Hashable, *args, **kwargs):
        self.source = source
        self.target = target

        super().__init__(
            f"node [{target} has no predecessors which are ancestors of node [{source}",
            *args,
            **kwargs,
        )


class ConstrainedGraph(AcyclicDiGraph):
    def remove_node_and_create_edges_from_predecessors_to_successors(
        self, node: Hashable
    ) -> None:
        # TODO: Account for case where this may lead to a
        # NoTargetPredecessorsAsSourceAncestorsError
        predecessors = self.predecessors(node=node)
        successors = self.successors(node=node)
        for predecessor, successor in itertools.product(predecessors, successors):
            super().add_edge(predecessor, successor)
        super().remove_node(node)

    def add_edge(self, source: Hashable, target: Hashable) -> None:
        for node in (source, target):
            if node not in self:
                raise NodeDoesNotExistError(node=node)

        if source == target:
            raise SelfLoopError(node=node)

        if not self.mimic and super().has_edge(source, target):
            raise EdgeExistsError(source=source, target=target)

        if nx.has_path(G=self, source=source, target=target):
            raise HasPathError(source=source, target=target, network=self)

        if self._is_successor_of_ancestor(source=source, target=target):
            raise SuccessorOfAncestorError(source=source, target=target, network=self)

        if self._adding_edge_introduces_cycle(source=source, target=target):
            raise EdgeIntroducesCycleError(source=source, target=target, network=self)

        super().add_edge(source, target)

    def get_target_predecessors_that_are_source_ancestors(
        self, source: Hashable, target: Hashable
    ) -> set:
        nodes_to_search = list(self.predecessors(node=source))
        found_nodes = set()
        searched_nodes = set()
        while nodes_to_search:
            node = nodes_to_search.pop()
            searched_nodes.add(node)
            if self.has_edge(node, target):
                found_nodes.add(node)
            else:
                predecessors = set(self.predecessors(node))
                unsearched_predecessors = predecessors - searched_nodes
                nodes_to_search.extend(unsearched_predecessors)

        if not found_nodes:
            raise NoTargetPredecessorsAsSourceAncestorsError(
                source=source, target=target
            )

        return found_nodes

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


def is_node_valid(node: Hashable) -> bool:
    """Check that a node name can be saved without causing problems"""
    # TODO: The type on this needs to be narrowed - move to io, as this is based
    # on the chosen delimiter?
    return "," not in json.dumps(node)
