import tkinter as tk
from collections.abc import Callable, Collection, Mapping, Sequence
from tkinter import ttk

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.helpers.failed_operation_window import (
    OperationFailedWindow,
)
from graft.layers.presentation.tkinter_gui.helpers.graph_edge_drawing_properties import (
    GraphEdgeDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.graph_node_drawing_properties import (
    GraphNodeDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.static_hierarchy_graph import (
    StaticHierarchyGraph,
)


class HierarchyGraphOperationFailedWindow(OperationFailedWindow):
    def __init__(
        self,
        master: tk.Misc,
        description_text: str,
        hierarchy_graph: tasks.IHierarchyGraphView,
        get_task_properties: Callable[[tasks.UID], GraphNodeDrawingProperties],
        get_hierarchy_properties: Callable[
            [tasks.UID, tasks.UID], GraphEdgeDrawingProperties
        ],
        get_task_annotation_text: Callable[[tasks.UID], str | None] | None = None,
        highlighted_task_groups: Sequence[
            tuple[str | None, GraphNodeDrawingProperties, Collection[tasks.UID]]
        ]
        | None = None,
        highlighted_hierarchy_groups: Sequence[
            tuple[
                str | None,
                GraphEdgeDrawingProperties,
                Collection[tuple[tasks.UID, tasks.UID]],
            ]
        ]
        | None = None,
        additional_hierarchy_groups: Sequence[
            tuple[
                str | None,
                GraphEdgeDrawingProperties,
                Collection[tuple[tasks.UID, tasks.UID]],
            ]
        ]
        | None = None,
        legend_elements: Sequence[
            tuple[str, GraphNodeDrawingProperties | GraphEdgeDrawingProperties]
        ]
        | None = None,
    ) -> None:
        def wrap_with_task_interceptor(
            get_task_properties: Callable[[tasks.UID], GraphNodeDrawingProperties],
            intercepted_task_to_properties_map: Mapping[
                tasks.UID, GraphNodeDrawingProperties
            ],
        ) -> Callable[[tasks.UID], GraphNodeDrawingProperties]:
            def inner(task: tasks.UID) -> GraphNodeDrawingProperties:
                if task in intercepted_task_to_properties_map:
                    return intercepted_task_to_properties_map[task]
                return get_task_properties(task)

            return inner

        def wrap_with_hierarchy_interceptor(
            get_hierarchy_properties: Callable[
                [tasks.UID, tasks.UID], GraphEdgeDrawingProperties
            ],
            intercepted_hierarchy_to_properties_map: Mapping[
                tuple[tasks.UID, tasks.UID], GraphEdgeDrawingProperties
            ],
        ) -> Callable[[tasks.UID, tasks.UID], GraphEdgeDrawingProperties]:
            def inner(
                supertask: tasks.UID, subtask: tasks.UID
            ) -> GraphEdgeDrawingProperties:
                if (supertask, subtask) in intercepted_hierarchy_to_properties_map:
                    return intercepted_hierarchy_to_properties_map[(supertask, subtask)]
                return get_hierarchy_properties(supertask, subtask)

            return inner

        def wrap_hierarchy_map_as_function(
            hierarchy_map: Mapping[
                tuple[tasks.UID, tasks.UID], GraphEdgeDrawingProperties
            ],
        ) -> Callable[[tasks.UID, tasks.UID], GraphEdgeDrawingProperties]:
            def inner(
                supertask: tasks.UID, subtask: tasks.UID
            ) -> GraphEdgeDrawingProperties:
                return hierarchy_map[(supertask, subtask)]

            return inner

        super().__init__(master=master)

        legend_elements_ = list(legend_elements) if legend_elements is not None else []

        if highlighted_task_groups is not None:
            highlighted_task_to_drawing_map = dict[
                tasks.UID, GraphNodeDrawingProperties
            ]()
            for label, drawing_properties, task_group in highlighted_task_groups:
                if label is not None:
                    legend_elements_.append((label, drawing_properties))
                for task in task_group:
                    highlighted_task_to_drawing_map[task] = drawing_properties
            get_task_properties_ = wrap_with_task_interceptor(
                get_task_properties=get_task_properties,
                intercepted_task_to_properties_map=highlighted_task_to_drawing_map,
            )
        else:
            get_task_properties_ = get_task_properties

        if highlighted_hierarchy_groups is not None:
            highlighted_hierarchies_to_properties_map = dict[
                tuple[tasks.UID, tasks.UID], GraphEdgeDrawingProperties
            ]()
            for (
                label,
                drawing_properties,
                hierarchy_group,
            ) in highlighted_hierarchy_groups:
                if label is not None:
                    legend_elements_.append((label, drawing_properties))
                for supertask, subtask in hierarchy_group:
                    highlighted_hierarchies_to_properties_map[(supertask, subtask)] = (
                        drawing_properties
                    )
            get_hierarchy_properties_ = wrap_with_hierarchy_interceptor(
                get_hierarchy_properties=get_hierarchy_properties,
                intercepted_hierarchy_to_properties_map=highlighted_hierarchies_to_properties_map,
            )
        else:
            get_hierarchy_properties_ = get_hierarchy_properties

        if additional_hierarchy_groups is not None:
            additional_hierarchies = set[tuple[tasks.UID, tasks.UID]]()
            additional_hierarchies_to_properties_map = dict[
                tuple[tasks.UID, tasks.UID], GraphEdgeDrawingProperties
            ]()
            for (
                label,
                drawing_properties,
                hierarchy_group,
            ) in additional_hierarchy_groups:
                if label is not None:
                    legend_elements_.append((label, drawing_properties))
                for supertask_and_subtask in hierarchy_group:
                    additional_hierarchies.add(supertask_and_subtask)
                    additional_hierarchies_to_properties_map[supertask_and_subtask] = (
                        drawing_properties
                    )
            get_additional_hierarchy_properties = wrap_hierarchy_map_as_function(
                additional_hierarchies_to_properties_map
            )
        else:
            additional_hierarchies = None
            get_additional_hierarchy_properties = None

        self._label = ttk.Label(self, text=description_text)

        self._graph = StaticHierarchyGraph(
            master=self,
            hierarchy_graph=hierarchy_graph,
            get_task_annotation_text=get_task_annotation_text,
            get_task_properties=get_task_properties_,
            get_hierarchy_properties=get_hierarchy_properties_,
            additional_hierarchies=additional_hierarchies,
            get_additional_hierarchy_properties=get_additional_hierarchy_properties,
            legend_elements=legend_elements_ or None,
        )

        self._label.grid(row=0, column=0)
        self._graph.grid(row=1, column=0)
