import itertools
from typing import Callable, Hashable, Iterable

import networkx as nx


class NodeExistsError(Exception):
    def __init__(self, node: Hashable, *args, **kwargs):
        self.node = node

        super().__init__(f"node [{node}] already exists", *args, **kwargs)


class NodeDoesNotExistError(Exception):
    def __init__(self, node: Hashable, *args, **kwargs):
        self.node = node

        super().__init__(f"node [{node}] does not exist", *args, **kwargs)


class InverseEdgeExistsError(Exception):
    def __init__(self, source: Hashable, target: Hashable, *args, **kwargs):
        self.source = source
        self.target = target

        super().__init__(
            f"edge from [{target}] -> [{source}] already exists, introduces two-node cycle",
            *args,
            **kwargs,
        )


class EdgeIntroducesCycleError(Exception):
    def __init__(
        self,
        source: Hashable,
        target: Hashable,
        network: "AcyclicDiGraph",
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


class PredecessorsError(Exception):
    def __init__(self, node: Hashable, graph: "AcyclicDiGraph", *args, **kwargs):
        self.node = node
        self.predecessors = set(graph.predecessors(node))

        formatted_predecessors = ", ".join(
            f"[{node}]" for node in sorted(self.predecessors)
        )

        super().__init__(
            f"node [{node}] has predecessors: {formatted_predecessors}", *args, **kwargs
        )


class SuccessorsError(Exception):
    def __init__(self, node: Hashable, graph: "AcyclicDiGraph", *args, **kwargs):
        self.node = node
        self.successors = set(graph.successors(node))

        formatted_successors = ", ".join(
            f"[{node}]" for node in sorted(self.successors)
        )

        super().__init__(
            f"node [{node}] has successors: {formatted_successors}", *args, **kwargs
        )


class SelfLoopError(Exception):
    def __init__(self, node: Hashable, *args, **kwargs):
        self.node = node

        super().__init__("No self loops allowed", *args, **kwargs)


class NotReachableError(Exception):
    def __init__(self, source: Hashable, target: Hashable, *args, **kwargs):
        self.source = source
        self.target = target

        super().__init__(
            f"node [{target} is not reachable from node [{source}", *args, **kwargs
        )


class AcyclicDiGraph(nx.DiGraph):
    def __init__(self, mimic: bool = True, *args, **kwargs):
        self.mimic = mimic  # Mimic behaviour of DiGraph for internal operations
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

        if not self.mimic and super().has_edge(target, source):
            raise InverseEdgeExistsError(source=source, target=target)

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

    def has_predecessors(self, node: Hashable) -> bool:
        try:
            predecessors = self.predecessors(node=node)
        except nx.NetworkXError as e:
            raise NodeDoesNotExistError(node=node) from e

        return any(True for _ in predecessors)

    def has_successors(self, node: Hashable) -> bool:
        try:
            successors = self.successors(node=node)
        except nx.NetworkXError as e:
            raise NodeDoesNotExistError(node=node) from e

        return any(True for _ in successors)

    def remove_node_and_neighbouring_edges(self, node: Hashable) -> None:
        try:
            super().remove_node(node)
        except nx.NetworkXError as e:
            raise NodeDoesNotExistError(node=node) from e

    def remove_node_and_create_edges_from_predecessors_to_successors(
        self, node: Hashable
    ) -> None:
        predecessors = self.predecessors(node=node)
        successors = self.successors(node=node)
        for predecessor, successor in itertools.product(predecessors, successors):
            super().add_edge(predecessor, successor)
        super().remove_node(node)

    def has_joining_subgraph(self, source: Hashable, target: Hashable) -> bool:
        """Check if a path from source to target exists."""
        for node in (source, target):
            if node not in self:
                raise NodeDoesNotExistError(node=node)

        return nx.has_path(G=self, source=source, target=target)

    def get_joining_subgraph(self, source: Hashable, target: Hashable) -> nx.DiGraph:
        """Get the subgraph that connects source to target."""
        # TODO: Find a more efficient solution
        subgraph = nx.DiGraph()
        for path in nx.all_simple_paths(G=self, source=source, target=target):
            for node1, node2 in zip(path, itertools.islice(path, 1, None)):
                subgraph.add_edge(node1, node2)

        if not subgraph:
            raise NotReachableError(source=source, target=target)

        return subgraph

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

        return True

    def relabel_node(self, old_label: Hashable, new_label: Hashable) -> None:
        if old_label not in self:
            raise NodeDoesNotExistError(node=old_label)
        if new_label in self:
            raise NodeExistsError(node=new_label)

        nx.relabel_nodes(self, {old_label: new_label}, copy=False)

    def direct_family_line(self, node: Hashable) -> set:
        """All ancestors, descendants and the node itself."""
        nodes = self.ancestors(node=node) | self.descendants(node=node)
        nodes.add(node)
        return nodes

    def descendants(self, node: Hashable) -> set:
        try:
            return nx.descendants(G=self, source=node)
        except nx.NetworkXError as e:
            raise NodeDoesNotExistError(node=node) from e

    def do_any_descendants_meet_condition(
        self, node: Hashable, condition_fn: Callable[[Hashable], bool]
    ) -> bool:
        """Do any descendants meet the condition?"""
        unsearched_nodes = set(self.successors(node=node))
        searched_nodes = set()
        while unsearched_nodes:
            current_node = unsearched_nodes.pop()
            if condition_fn(current_node):
                return True
            searched_nodes.add(current_node)
            supertasks = set(self.successors(node=current_node))
            supertasks.difference_update(searched_nodes)
            unsearched_nodes.update(supertasks)

        return False

    def ancestors(self, node: Hashable) -> set:
        try:
            return nx.ancestors(G=self, source=node)
        except nx.NetworkXError as e:
            raise NodeDoesNotExistError(node=node) from e

    def do_any_ancestors_meet_condition(
        self, node: Hashable, condition_fn: Callable[[Hashable], bool]
    ) -> bool:
        """Do any ancestors meet the condition?"""
        unsearched_nodes = set(self.predecessors(node=node))
        searched_nodes = set()
        while unsearched_nodes:
            current_node = unsearched_nodes.pop()
            if condition_fn(current_node):
                return True
            searched_nodes.add(current_node)
            supertasks = set(self.predecessors(node=current_node))
            supertasks.difference_update(searched_nodes)
            unsearched_nodes.update(supertasks)

        return False

    def predecessors(self, node: Hashable) -> Iterable[Hashable]:
        try:
            return super().predecessors(n=node)
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
