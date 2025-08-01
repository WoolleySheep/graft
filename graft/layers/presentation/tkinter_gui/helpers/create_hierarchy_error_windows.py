from collections.abc import Callable
from tkinter import Misc

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import domain_visual_language
from graft.layers.presentation.tkinter_gui.helpers.colour import (
    GREEN,
    ORANGE,
    PURPLE,
    RED,
    WHITE,
    YELLOW,
)
from graft.layers.presentation.tkinter_gui.helpers.hierarchy_graph_failed_operation_window import (
    HierarchyGraphOperationFailedWindow,
)
from graft.layers.presentation.tkinter_gui.helpers.network_graph_failed_operation_window import (
    NetworkGraphOperationFailedWindow,
)
from graft.layers.presentation.tkinter_gui.helpers.static_graph import (
    format_task_name_for_annotation,
)


def convert_create_hierarchy_exceptions_to_error_windows(
    func: Callable[[], None],
    get_task_name: Callable[[tasks.UID], tasks.Name],
    master: Misc,
) -> bool:
    """Catch task hierarchy creation exceptions and display the matching error window.

    If the fuction succeeds, returns True. If the function raises an exception and an
    error window is shown, return False.
    """
    try:
        func()
    except tasks.TaskDoesNotExistError as e:
        HierarchyGraphOperationFailedWindow(
            master=master,
            description_text=f"Cannot create a hierarchy as task [{e.task}] does not exist",
            hierarchy_graph=tasks.HierarchyGraph(),
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(),
        )
        return False
    except tasks.HierarchyLoopError as e:
        hierarchy_graph = tasks.HierarchyGraph([(e.task, set())])
        HierarchyGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a hierarchy between a task and itself",
            hierarchy_graph=hierarchy_graph,
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            additional_hierarchy_groups=[
                (
                    None,
                    domain_visual_language.get_graph_edge_properties(colour=RED),
                    {(e.task, e.task)},
                )
            ],
        )
        return False
    except tasks.HierarchyAlreadyExistsError as e:
        hierarchy_graph = tasks.HierarchyGraph([(e.supertask, {e.subtask})])
        HierarchyGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a hierarchy that already exists",
            hierarchy_graph=hierarchy_graph,
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_hierarchy_groups=[
                (
                    None,
                    domain_visual_language.get_graph_edge_properties(colour=RED),
                    {(e.supertask, e.subtask)},
                )
            ],
        )
        return False
    except tasks.HierarchyIntroducesCycleError as e:
        HierarchyGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a hierarchy that introduces a hierarchy cycle",
            hierarchy_graph=e.connecting_subgraph,
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    "supertask",
                    domain_visual_language.get_graph_node_properties(colour=RED),
                    {e.supertask},
                ),
                (
                    "subtask",
                    domain_visual_language.get_graph_node_properties(colour=YELLOW),
                    {e.subtask},
                ),
            ],
            additional_hierarchy_groups=[
                (
                    "proposed hierarchy",
                    domain_visual_language.get_graph_edge_properties(
                        colour=ORANGE,
                        connection_style=domain_visual_language.CURVED_ARROW_CONNECTION_STYLE,
                    ),
                    {(e.supertask, e.subtask)},
                )
            ],
        )
        return False

    except tasks.HierarchyIntroducesRedundantHierarchyError as e:
        HierarchyGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a hierarchy that introduces a redundant hierarchy",
            hierarchy_graph=e.connecting_subgraph,
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    "supertask",
                    domain_visual_language.get_graph_node_properties(colour=RED),
                    {e.supertask},
                ),
                (
                    "subtask",
                    domain_visual_language.get_graph_node_properties(colour=YELLOW),
                    {e.subtask},
                ),
            ],
            additional_hierarchy_groups=[
                (
                    "proposed hierarchy",
                    domain_visual_language.get_graph_edge_properties(
                        colour=ORANGE,
                        connection_style=domain_visual_language.CURVED_ARROW_CONNECTION_STYLE,
                    ),
                    {(e.supertask, e.subtask)},
                )
            ],
        )
        return False

    except tasks.HierarchyIntroducesNetworkCycleError as e:
        NetworkGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a hierarchy that introduces a network cycle",
            task_network=e.connecting_subgraph,
            get_task_properties=lambda _: domain_visual_language.get_network_task_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_network_hierarchy_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_dependency_properties=lambda _,
            __: domain_visual_language.get_network_dependency_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    "supertask",
                    domain_visual_language.get_network_task_properties(colour=RED),
                    {e.supertask},
                ),
                (
                    "subtask",
                    domain_visual_language.get_network_task_properties(colour=YELLOW),
                    {e.subtask},
                ),
            ],
            additional_hierarchy_groups=[
                (
                    "proposed hierarchy",
                    domain_visual_language.get_network_hierarchy_properties(
                        colour=ORANGE,
                        alpha_level=domain_visual_language.NetworkAlphaLevel.VERY_HIGHLIGHTED,
                        connection_style=domain_visual_language.CURVED_ARROW_CONNECTION_STYLE,
                    ),
                    {(e.supertask, e.subtask)},
                )
            ],
            legend_elements=[
                (
                    "dependency",
                    domain_visual_language.get_network_dependency_properties(),
                ),
                (
                    "hierarchy",
                    domain_visual_language.get_network_hierarchy_properties(),
                ),
            ],
        )
        return False

    except tasks.HierarchyIntroducesDependencyDuplicationError as e:
        NetworkGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a hierarchy that introduces a dependency duplication",
            task_network=e.connecting_subgraph,
            get_task_properties=lambda _: domain_visual_language.get_network_task_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_network_hierarchy_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_dependency_properties=lambda _,
            __: domain_visual_language.get_network_dependency_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    "supertask",
                    domain_visual_language.get_network_task_properties(colour=RED),
                    {e.supertask},
                ),
                (
                    "subtask",
                    domain_visual_language.get_network_task_properties(colour=YELLOW),
                    {e.subtask},
                ),
            ],
            additional_hierarchy_groups=[
                (
                    "proposed hierarchy",
                    domain_visual_language.get_network_hierarchy_properties(
                        colour=ORANGE,
                        alpha_level=domain_visual_language.NetworkAlphaLevel.VERY_HIGHLIGHTED,
                        connection_style=domain_visual_language.CURVED_ARROW_CONNECTION_STYLE,
                    ),
                    {(e.supertask, e.subtask)},
                )
            ],
            legend_elements=[
                (
                    "dependency",
                    domain_visual_language.get_network_dependency_properties(),
                ),
                (
                    "hierarchy",
                    domain_visual_language.get_network_hierarchy_properties(),
                ),
            ],
        )
        return False

    except tasks.HierarchyIntroducesDependencyCrossoverError as e:
        NetworkGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a hierarchy that introduces a dependency crossover",
            task_network=e.connecting_subgraph,
            get_task_properties=lambda _: domain_visual_language.get_network_task_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_network_hierarchy_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_dependency_properties=lambda _,
            __: domain_visual_language.get_network_dependency_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    "supertask",
                    domain_visual_language.get_network_task_properties(colour=RED),
                    {e.supertask},
                ),
                (
                    "subtask",
                    domain_visual_language.get_network_task_properties(colour=YELLOW),
                    {e.subtask},
                ),
            ],
            additional_hierarchy_groups=[
                (
                    "proposed hierarchy",
                    domain_visual_language.get_network_hierarchy_properties(
                        colour=ORANGE,
                        alpha_level=domain_visual_language.NetworkAlphaLevel.VERY_HIGHLIGHTED,
                        connection_style=domain_visual_language.CURVED_ARROW_CONNECTION_STYLE,
                    ),
                    {(e.supertask, e.subtask)},
                )
            ],
            legend_elements=[
                (
                    "dependency",
                    domain_visual_language.get_network_dependency_properties(),
                ),
                (
                    "hierarchy",
                    domain_visual_language.get_network_hierarchy_properties(),
                ),
            ],
        )
        return False

    except tasks.MultipleImportancesInHierarchyError as e:
        hierarchy_graph = e.subsystem.network_graph().hierarchy_graph().clone()
        hierarchy_graph.add_hierarchy(e.supertask, e.subtask)
        attributes_register = e.subsystem.attributes_register()  # Bind to local scope
        HierarchyGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a hierarchy that introduces an inferred importance for tasks that already have a concrete importance",
            hierarchy_graph=hierarchy_graph,
            get_task_properties=lambda task: domain_visual_language.get_graph_node_properties(
                colour=domain_visual_language.get_task_colour_by_importance(
                    importance=attributes_register[task].importance
                ),
                alpha_level=domain_visual_language.GraphAlphaLevel.DEFAULT
                if attributes_register[task].importance is not None
                else domain_visual_language.GraphAlphaLevel.FADED,
            ),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(
                alpha_level=domain_visual_language.GraphAlphaLevel.FADED
            ),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    None,
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.get_task_colour_by_importance(
                            importance=e.subsystem.attributes_register()[
                                e.supertask
                            ].importance
                        ),
                        edge_colour=GREEN,
                    ),
                    {e.supertask},
                ),
                (
                    None,
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.get_task_colour_by_importance(
                            importance=e.subsystem.attributes_register()[
                                e.subtask
                            ].importance
                        ),
                        edge_colour=PURPLE,
                    ),
                    {e.subtask},
                ),
            ],
            additional_hierarchy_groups=[
                (
                    "proposed hierarchy",
                    domain_visual_language.get_graph_edge_properties(
                        colour=ORANGE,
                        connection_style=domain_visual_language.CURVED_ARROW_CONNECTION_STYLE,
                    ),
                    {(e.supertask, e.subtask)},
                )
            ],
            legend_elements=[
                (
                    "high importance",
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.HIGH_IMPORTANCE_COLOUR
                    ),
                ),
                (
                    "medium importance",
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.MEDIUM_IMPORTANCE_COLOUR
                    ),
                ),
                (
                    "low importance",
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.LOW_IMPORTANCE_COLOUR
                    ),
                ),
                (
                    "supertask",
                    domain_visual_language.get_graph_node_properties(
                        colour=WHITE, edge_colour=GREEN
                    ),
                ),
                (
                    "subtask",
                    domain_visual_language.get_graph_node_properties(
                        colour=WHITE, edge_colour=PURPLE
                    ),
                ),
                (
                    "hierarchy",
                    domain_visual_language.get_graph_edge_properties(),
                ),
            ],
        )
        return False

    except tasks.UpstreamTasksOfSupertaskAreIncompleteError as e:
        network_graph = e.subsystem.network_graph().clone()
        network_graph.add_hierarchy(e.supertask, e.subtask)
        subsytem = e.subsystem  # Bind to local scope
        upstream_task_incomplete_map = (
            e.upstream_task_incomplete_map
        )  # Bind to local scope
        NetworkGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a hierarchy as the subtask has started, but upstream tasks are incomplete",
            task_network=network_graph,
            get_task_properties=lambda task: domain_visual_language.get_network_task_properties(
                colour=domain_visual_language.get_task_colour_by_progress(
                    subsytem.get_progress(task)
                ),
                alpha_level=domain_visual_language.NetworkAlphaLevel.DEFAULT
                if task in upstream_task_incomplete_map
                else domain_visual_language.NetworkAlphaLevel.VERY_FADED,
            ),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_network_hierarchy_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_dependency_properties=lambda _,
            __: domain_visual_language.get_network_dependency_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    None,
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.NOT_STARTED_TASK_COLOUR,
                        edge_colour=RED,
                        alpha_level=domain_visual_language.NetworkAlphaLevel.HIGHLIGHTED,
                    ),
                    {e.supertask},
                ),
                (
                    None,
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.get_task_colour_by_progress(
                            e.subtask_progress
                        ),
                        edge_colour=PURPLE,
                        alpha_level=domain_visual_language.NetworkAlphaLevel.HIGHLIGHTED,
                    ),
                    {e.subtask},
                ),
            ],
            highlighted_hierarchy_groups=[
                (
                    "proposed hierarchy",
                    domain_visual_language.get_network_hierarchy_properties(
                        colour=ORANGE,
                        alpha_level=domain_visual_language.NetworkAlphaLevel.HIGHLIGHTED,
                        connection_style=domain_visual_language.CURVED_ARROW_CONNECTION_STYLE,
                    ),
                    {(e.supertask, e.subtask)},
                )
            ],
            legend_elements=[
                (
                    "completed",
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.COMPLETED_TASK_COLOUR
                    ),
                ),
                (
                    "in progress",
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.IN_PROGRESS_TASK_COLOUR
                    ),
                ),
                (
                    "not started",
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.NOT_STARTED_TASK_COLOUR
                    ),
                ),
                (
                    "supertask",
                    domain_visual_language.get_network_task_properties(
                        colour=WHITE, edge_colour=RED
                    ),
                ),
                (
                    "subtask",
                    domain_visual_language.get_network_task_properties(
                        colour=WHITE, edge_colour=PURPLE
                    ),
                ),
                (
                    "dependency",
                    domain_visual_language.get_network_dependency_properties(),
                ),
                (
                    "hierarchy",
                    domain_visual_language.get_network_hierarchy_properties(),
                ),
            ],
        )
        return False

    except tasks.DownstreamTasksOfSupertaskHaveStartedError as e:
        network_graph = e.subsystem.network_graph().clone()
        network_graph.add_hierarchy(e.supertask, e.subtask)
        subsystem = e.subsystem  # Bind to local scope
        downstream_task_started_map = (
            e.downstream_task_started_map
        )  # Bind to local scope
        NetworkGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a hierarchy as the subtask is incomplete, but downstream tasks have started",
            task_network=network_graph,
            get_task_properties=lambda task: domain_visual_language.get_network_task_properties(
                colour=domain_visual_language.get_task_colour_by_progress(
                    subsystem.get_progress(task)
                ),
                alpha_level=domain_visual_language.NetworkAlphaLevel.DEFAULT
                if task in downstream_task_started_map
                else domain_visual_language.NetworkAlphaLevel.VERY_FADED,
            ),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_network_hierarchy_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_dependency_properties=lambda _,
            __: domain_visual_language.get_network_dependency_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    None,
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.COMPLETED_TASK_COLOUR,
                        edge_colour=RED,
                        alpha_level=domain_visual_language.NetworkAlphaLevel.HIGHLIGHTED,
                    ),
                    {e.supertask},
                ),
                (
                    None,
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.get_task_colour_by_progress(
                            e.subtask_progress
                        ),
                        edge_colour=PURPLE,
                        alpha_level=domain_visual_language.NetworkAlphaLevel.HIGHLIGHTED,
                    ),
                    {e.subtask},
                ),
            ],
            highlighted_hierarchy_groups=[
                (
                    "proposed hierarchy",
                    domain_visual_language.get_network_hierarchy_properties(
                        colour=ORANGE,
                        alpha_level=domain_visual_language.NetworkAlphaLevel.HIGHLIGHTED,
                        connection_style=domain_visual_language.CURVED_ARROW_CONNECTION_STYLE,
                    ),
                    {(e.supertask, e.subtask)},
                )
            ],
            legend_elements=[
                (
                    "completed",
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.COMPLETED_TASK_COLOUR
                    ),
                ),
                (
                    "in progress",
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.IN_PROGRESS_TASK_COLOUR
                    ),
                ),
                (
                    "not started",
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.NOT_STARTED_TASK_COLOUR
                    ),
                ),
                (
                    "supertask",
                    domain_visual_language.get_network_task_properties(
                        colour=WHITE, edge_colour=RED
                    ),
                ),
                (
                    "subtask",
                    domain_visual_language.get_network_task_properties(
                        colour=WHITE, edge_colour=PURPLE
                    ),
                ),
                (
                    "dependency",
                    domain_visual_language.get_network_dependency_properties(),
                ),
                (
                    "hierarchy",
                    domain_visual_language.get_network_hierarchy_properties(),
                ),
            ],
        )
        return False

    except tasks.MismatchedProgressForNewSupertaskError as e:
        hierarchy_graph = tasks.HierarchyGraph(
            [(e.supertask, [e.subtask]), (e.subtask, [])]
        )
        HierarchyGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a hierarchy as the supertask (which is concrete), has a different progress than the subtask",
            hierarchy_graph=hierarchy_graph,
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(
                colour=ORANGE,
                connection_style=domain_visual_language.CURVED_ARROW_CONNECTION_STYLE,
            ),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    None,
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.get_task_colour_by_progress(
                            e.supertask_progress
                        ),
                        edge_colour=GREEN,
                    ),
                    {e.supertask},
                ),
                (
                    None,
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.get_task_colour_by_progress(
                            e.subtask_progress
                        ),
                        edge_colour=PURPLE,
                    ),
                    {e.subtask},
                ),
            ],
            legend_elements=[
                (
                    "completed",
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.COMPLETED_TASK_COLOUR
                    ),
                ),
                (
                    "in progress",
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.IN_PROGRESS_TASK_COLOUR
                    ),
                ),
                (
                    "not started",
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.NOT_STARTED_TASK_COLOUR
                    ),
                ),
                (
                    "supertask",
                    domain_visual_language.get_graph_node_properties(
                        colour=WHITE, edge_colour=GREEN
                    ),
                ),
                (
                    "subtask",
                    domain_visual_language.get_graph_node_properties(
                        colour=WHITE, edge_colour=PURPLE
                    ),
                ),
                (
                    "proposed hierarchy",
                    domain_visual_language.get_graph_edge_properties(
                        colour=ORANGE,
                    ),
                ),
            ],
        )
        return False
    return True
