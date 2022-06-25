from typing import Mapping

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import networkx as nx

from graft.constrained_graph import ConstrainedGraph
from graft.task_attributes import TaskAttributes
from graft.task_tag_table import TaskTagTable

TAG_NODE_DEFAULT_SIZE = 70
TASK_NODE_DEFAULT_SIZE = 300
# https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_networkx_nodes.html

# TODO: Create 3D task network visualisation
# TODO: Change node circles to rectangles


def draw_y(
    tag_hierarchy: ConstrainedGraph,
    task_tag_table: TaskTagTable,
    task_attributes_map: Mapping[str, TaskAttributes],
) -> None:
    """Draw tag hierarchy on the left, and task-tag pairs on the right."""
    # TODO: Rename function to be more descriptive
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(7, 5))

    fig.suptitle("Tag network")
    ax1.set_title("Tag hierarchy")
    ax2.set_title("Tag-task pairs")

    node_sizes1 = [
        TAG_NODE_DEFAULT_SIZE * len(label) ** 2 for label in tag_hierarchy.nodes()
    ]
    pos1 = nx.drawing.nx_pydot.pydot_layout(tag_hierarchy, prog="dot")
    nx.draw(tag_hierarchy, pos=pos1, ax=ax1, with_labels=True, node_size=node_sizes1)

    # TODO: Account for case where tag and task potentially have the same name
    task_tag_pair_graph = nx.DiGraph()
    task_tag_pair_graph.graph["graph"] = {"rankdir": "RL"}

    for task, tag in task_tag_table.data:
        task_w_name = f"{task}: {task_attributes_map[task].name}"
        tag_node = f"tag-{tag}"
        task_node = f"task-{task_w_name}"
        task_tag_pair_graph.add_edge(task_node, tag_node)

    node_sizes = []
    node_labels = {}
    for node in task_tag_pair_graph.nodes():
        prefix_len = len("tag-") if node.startswith("tag-") else len("task-")
        node_label = node[prefix_len:]
        node_labels[node] = node_label
        node_size = TAG_NODE_DEFAULT_SIZE * len(node_label) ** 2
        node_sizes.append(node_size)

    # TODO: Work out why reversing the edge ordered causes 'dot' to go mad
    pos2 = nx.drawing.nx_pydot.pydot_layout(G=task_tag_pair_graph, prog="dot")
    nx.draw(
        G=task_tag_pair_graph,
        arrows=False,
        pos=pos2,
        ax=ax2,
        with_labels=True,
        node_size=node_sizes,
        labels=node_labels,
    )

    plt.show()


def draw_x(
    task_hierarchy_digraph: nx.DiGraph,
    task_dependencies_digraph: nx.DiGraph,
    task_attributes_map: Mapping[int, TaskAttributes],
) -> None:
    # TODO: Rename function to be more descriptive
    fig = plt.figure(figsize=(7, 5))

    plt.subplots_adjust(
        top=0.9, bottom=0.05, right=0.95, left=0.05, hspace=0.15, wspace=0.1
    )

    gs = gridspec.GridSpec(nrows=2, ncols=3, figure=fig)

    ax_top_left = fig.add_subplot(gs[0, :2])
    ax_bottom_left = fig.add_subplot(gs[1, :2])
    ax_right = fig.add_subplot(gs[:, 2])

    ax_top_left.margins(0.1)
    ax_bottom_left.margins(0.1)

    fig.suptitle("Task Network")
    ax_top_left.set_title("Task Hierarchy")
    ax_bottom_left.set_title("Task Dependencies")
    ax_right.set_title("Task Name Index")

    uid_and_attributes = sorted(task_attributes_map.items(), key=lambda x: x[0])
    text = ["TASK: NAME", "-------  --------"]
    for uid, attributes in uid_and_attributes:
        text.append(f"{uid:>7}: {attributes.name}")
    text = "\n".join(text)

    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle="square", facecolor="w")

    # place a text box in upper left in axes coords
    # TODO: Fix ordering - 10 is appearing before 2 due to string format
    ax_right.text(
        0.05,
        0.985,
        text,
        transform=ax_right.transAxes,
        fontsize=14,
        verticalalignment="top",
        wrap=True,
        bbox=props,
    )

    ax_right.set_in_layout(False)

    ax_right.axis("off")

    hierarchy_node_sizes = [
        len(label) ** 2 * TASK_NODE_DEFAULT_SIZE
        for label in task_hierarchy_digraph.nodes()
    ]
    dependency_node_sizes = [
        len(label) ** 2 * TASK_NODE_DEFAULT_SIZE
        for label in task_dependencies_digraph.nodes()
    ]

    task_dependencies_digraph.graph["graph"] = {"rankdir": "LR"}

    hierarchy_pos = nx.drawing.nx_pydot.pydot_layout(task_hierarchy_digraph, prog="dot")
    nx.draw(
        task_hierarchy_digraph,
        pos=hierarchy_pos,
        ax=ax_top_left,
        with_labels=True,
        node_size=hierarchy_node_sizes,
    )
    ax_top_left.axis("on")

    dependencies_pos = nx.drawing.nx_pydot.pydot_layout(
        task_dependencies_digraph, prog="dot"
    )
    nx.draw(
        G=task_dependencies_digraph,
        pos=dependencies_pos,
        ax=ax_bottom_left,
        with_labels=True,
        node_size=dependency_node_sizes,
    )
    ax_bottom_left.axis("on")

    plt.show()
