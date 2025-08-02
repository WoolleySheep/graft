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
from graft.layers.presentation.tkinter_gui.helpers.dependency_graph_failed_operation_window import (
    DependencyGraphOperationFailedWindow,
)
from graft.layers.presentation.tkinter_gui.helpers.network_graph_failed_operation_window import (
    NetworkGraphOperationFailedWindow,
)
from graft.layers.presentation.tkinter_gui.helpers.static_graph import (
    format_task_name_for_annotation,
)


def convert_create_dependency_exceptions_to_error_windows(
    func: Callable[[], None],
    get_task_name: Callable[[tasks.UID], tasks.Name],
    master: Misc,
) -> bool:
    """Catch task dependency creation exceptions and display the matching error window.

    If the function succeeds, returns True. If the function raises an exception and an
    error window is shown, return False.
    """
    try:
        func()
    except tasks.TaskDoesNotExistError as e:
        DependencyGraphOperationFailedWindow(
            master=master,
            description_text=f"Cannot create a dependency as task [{e.task}] does not exist",
            dependency_graph=tasks.DependencyGraph(),
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_dependency_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(),
        )
        return False
    except tasks.DependencyLoopError as e:
        dependency_graph = tasks.DependencyGraph([(e.task, set())])
        DependencyGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a dependency between a task and itself",
            dependency_graph=dependency_graph,
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_dependency_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            additional_dependency_groups=[
                (
                    None,
                    domain_visual_language.get_graph_edge_properties(colour=RED),
                    {(e.task, e.task)},
                )
            ],
        )
        return False
    except tasks.DependencyAlreadyExistsError as e:
        dependency_graph = tasks.DependencyGraph(
            [(e.dependee_task, [e.dependent_task]), (e.dependent_task, [])]
        )
        DependencyGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a dependency that already exists",
            dependency_graph=dependency_graph,
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_dependency_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_dependency_groups=[
                (
                    None,
                    domain_visual_language.get_graph_edge_properties(colour=RED),
                    {(e.dependee_task, e.dependent_task)},
                )
            ],
        )
        return False
    except tasks.DependencyIntroducesCycleError as e:
        DependencyGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a dependency that introduces a dependency cycle",
            dependency_graph=e.connecting_subgraph,
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_dependency_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    "dependee-task",
                    domain_visual_language.get_graph_node_properties(colour=RED),
                    {e.dependee_task},
                ),
                (
                    "dependent-task",
                    domain_visual_language.get_graph_node_properties(colour=YELLOW),
                    {e.dependent_task},
                ),
            ],
            additional_dependency_groups=[
                (
                    "proposed dependency",
                    domain_visual_language.get_graph_edge_properties(
                        colour=ORANGE,
                        connection_style=domain_visual_language.CURVED_ARROW_CONNECTION_STYLE,
                    ),
                    {(e.dependee_task, e.dependent_task)},
                )
            ],
        )
        return False
    except tasks.DependencyIntroducesNetworkCycleError as e:
        NetworkGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a dependency that introduces a network cycle",
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
                    "dependee-task",
                    domain_visual_language.get_network_task_properties(colour=RED),
                    {e.dependee_task},
                ),
                (
                    "dependent-task",
                    domain_visual_language.get_network_task_properties(colour=YELLOW),
                    {e.dependent_task},
                ),
            ],
            additional_dependency_groups=[
                (
                    "proposed dependency",
                    domain_visual_language.get_network_dependency_properties(
                        colour=ORANGE,
                        alpha_level=domain_visual_language.NetworkAlphaLevel.VERY_HIGHLIGHTED,
                        connection_style=domain_visual_language.CURVED_ARROW_CONNECTION_STYLE,
                    ),
                    {(e.dependee_task, e.dependent_task)},
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
    except tasks.DependencyIntroducesDependencyDuplicationError as e:
        unconstrained_subgraph = tasks.get_unconstrained_graph(e.connecting_subgraph)
        unconstrained_subgraph.add_dependency(
            dependee_task=e.dependee_task, dependent_task=e.dependent_task
        )
        NetworkGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a dependency that introduces a dependency duplication",
            task_network=unconstrained_subgraph,
            get_task_properties=lambda _: domain_visual_language.get_network_task_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_network_hierarchy_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_dependency_properties=lambda _,
            __: domain_visual_language.get_network_dependency_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.DEFAULT
            ),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    "dependee-task",
                    domain_visual_language.get_network_task_properties(colour=RED),
                    {e.dependee_task},
                ),
                (
                    "dependent-task",
                    domain_visual_language.get_network_task_properties(colour=YELLOW),
                    {e.dependent_task},
                ),
            ],
            highlighted_dependency_groups=[
                (
                    "proposed dependency",
                    domain_visual_language.get_network_dependency_properties(
                        colour=ORANGE,
                        alpha_level=domain_visual_language.NetworkAlphaLevel.VERY_HIGHLIGHTED,
                        connection_style=domain_visual_language.CURVED_ARROW_CONNECTION_STYLE,
                    ),
                    {(e.dependee_task, e.dependent_task)},
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
    except tasks.DependencyIntroducesDependencyCrossoverError as e:
        unconstrained_subgraph = tasks.get_unconstrained_graph(e.connecting_subgraph)
        unconstrained_subgraph.add_dependency(
            dependee_task=e.dependee_task, dependent_task=e.dependent_task
        )
        NetworkGraphOperationFailedWindow(
            master=master,
            description_text="Cannot create a dependency that introduces a dependency crossover",
            task_network=unconstrained_subgraph,
            get_task_properties=lambda _: domain_visual_language.get_network_task_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_network_hierarchy_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_dependency_properties=lambda _,
            __: domain_visual_language.get_network_dependency_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.DEFAULT
            ),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    "dependee-task",
                    domain_visual_language.get_network_task_properties(colour=RED),
                    {e.dependee_task},
                ),
                (
                    "dependent-task",
                    domain_visual_language.get_network_task_properties(colour=YELLOW),
                    {e.dependent_task},
                ),
            ],
            highlighted_dependency_groups=[
                (
                    "proposed dependency",
                    domain_visual_language.get_network_dependency_properties(
                        colour=ORANGE,
                        alpha_level=domain_visual_language.NetworkAlphaLevel.VERY_HIGHLIGHTED,
                        connection_style=domain_visual_language.CURVED_ARROW_CONNECTION_STYLE,
                    ),
                    {(e.dependee_task, e.dependent_task)},
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
    except tasks.DependeeIncompleteDependentStartedError as e:
        dependency_graph = tasks.DependencyGraph(
            [(e.dependee_task, [e.dependent_task]), (e.dependent_task, [])]
        )
        DependencyGraphOperationFailedWindow(
            master=master,
            dependency_graph=dependency_graph,
            description_text="Cannot create a dependency when the dependee task is incomplete and the dependent task has started",
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_dependency_properties=lambda _,
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
                            e.dependee_progress
                        ),
                        edge_colour=GREEN,
                    ),
                    {e.dependee_task},
                ),
                (
                    None,
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.get_task_colour_by_progress(
                            e.dependent_progress
                        ),
                        edge_colour=PURPLE,
                    ),
                    {e.dependent_task},
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
                    "dependee-task",
                    domain_visual_language.get_graph_node_properties(
                        colour=WHITE, edge_colour=GREEN
                    ),
                ),
                (
                    "dependent-task",
                    domain_visual_language.get_graph_node_properties(
                        colour=WHITE, edge_colour=PURPLE
                    ),
                ),
                (
                    "proposed dependency",
                    domain_visual_language.get_graph_edge_properties(
                        colour=ORANGE,
                    ),
                ),
            ],
        )
        return False
    return True
