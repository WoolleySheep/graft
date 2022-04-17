from typing import Mapping

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import networkx as nx

from graft.task_attributes import TaskAttributes

TAG_NODE_DEFAULT_SIZE = 70
TASK_NODE_DEFAULT_SIZE = 300
# https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_networkx_nodes.html


def draw_hierarchical_digraph(digraph: nx.DiGraph) -> None:
    # TODO: Rename to something more descriptive
    # TODO: Change from circles to ovals for longer names
    node_sizes = [len(label) ** 2 * TAG_NODE_DEFAULT_SIZE for label in digraph.nodes()]
    pos = nx.drawing.nx_pydot.pydot_layout(digraph, prog="dot")
    nx.draw(digraph, pos=pos, with_labels=True, node_size=node_sizes)
    plt.show()


def draw_x(
    task_hierarchy_digraph: nx.DiGraph,
    task_dependencies_digraph: nx.DiGraph,
    task_attributes_map: Mapping[int, TaskAttributes],
) -> None:

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

    uid_and_attributes = sorted(task_attributes_map.items(), key=lambda x: x[0])
    text = ["TASK: NAME", "-------  --------"]
    for uid, attributes in uid_and_attributes:
        text.append(f"{uid:>7}: {attributes.name}")
    text = "\n".join(text)

    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle="square", facecolor="w")

    # place a text box in upper left in axes coords
    ax_right.text(
        0.05,
        1,
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
        task_dependencies_digraph,
        pos=dependencies_pos,
        ax=ax_bottom_left,
        with_labels=True,
        node_size=dependency_node_sizes,
    )
    ax_bottom_left.axis("on")

    plt.show()
