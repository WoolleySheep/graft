from collections.abc import Hashable

import networkx as nx

from graft import graphs
from graft.domain import tasks


def convert_hierarchy_to_reduced_dag(
    graph: tasks.IHierarchyGraphView,
) -> graphs.ReducedDAG[tasks.UID]:
    reduced_dag = graphs.ReducedDAG[tasks.UID]()
    for task in graph.tasks():
        reduced_dag.add_node(task)
    for parent, child in graph.hierarchies():
        reduced_dag.add_edge(parent, child)
    return reduced_dag


def convert_dependency_to_dag(
    graph: tasks.IDependencyGraphView,
) -> graphs.DirectedAcyclicGraph[tasks.UID]:
    dag = graphs.DirectedAcyclicGraph[tasks.UID]()
    for task in graph.tasks():
        dag.add_node(task)
    for parent, child in graph.dependencies():
        dag.add_edge(parent, child)
    return dag


def convert_simple_digraph_to_nx_digraph[T: Hashable](
    graph: graphs.SimpleDiGraph[T],
) -> nx.DiGraph:
    nx_digraph = nx.DiGraph()
    for node in graph.nodes():
        nx_digraph.add_node(node)
    for parent, child in graph.edges():
        nx_digraph.add_edge(parent, child)
    return nx_digraph
