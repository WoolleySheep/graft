import tkinter as tk
from collections.abc import Callable, Collection, Mapping, Sequence
from tkinter import ttk

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.helpers.failed_operation_window import (
    OperationFailedWindow,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.network_task_drawing_properties import (
    NetworkTaskDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.relationship_drawing_properties import (
    NetworkRelationshipDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.static_task_network_graph import (
    AdditionalRelationships,
    StaticTaskNetworkGraph,
)


class NetworkGraphOperationFailedWindow(OperationFailedWindow):
    def __init__(
        self,
        master: tk.Misc,
        description_text: str,
        task_network: tasks.INetworkGraphView,
        get_task_properties: Callable[[tasks.UID], NetworkTaskDrawingProperties],
        get_hierarchy_properties: Callable[
            [tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties
        ],
        get_dependency_properties: Callable[
            [tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties
        ],
        get_task_annotation_text: Callable[[tasks.UID], str | None],
        highlighted_task_groups: Sequence[
            tuple[str | None, NetworkTaskDrawingProperties, Collection[tasks.UID]]
        ]
        | None = None,
        highlighted_hierarchy_groups: Sequence[
            tuple[
                str | None,
                NetworkRelationshipDrawingProperties,
                Collection[tuple[tasks.UID, tasks.UID]],
            ]
        ]
        | None = None,
        highlighted_dependency_groups: Sequence[
            tuple[
                str | None,
                NetworkRelationshipDrawingProperties,
                Collection[tuple[tasks.UID, tasks.UID]],
            ]
        ]
        | None = None,
        additional_hierarchy_groups: Sequence[
            tuple[
                str | None,
                NetworkRelationshipDrawingProperties,
                Collection[tuple[tasks.UID, tasks.UID]],
            ]
        ]
        | None = None,
        additional_dependency_groups: Sequence[
            tuple[
                str | None,
                NetworkRelationshipDrawingProperties,
                Collection[tuple[tasks.UID, tasks.UID]],
            ]
        ]
        | None = None,
        legend_elements: Sequence[
            tuple[
                str, NetworkTaskDrawingProperties | NetworkRelationshipDrawingProperties
            ]
        ]
        | None = None,
    ) -> None:
        def wrap_with_task_interceptor(
            get_task_properties: Callable[[tasks.UID], NetworkTaskDrawingProperties],
            intercepted_task_to_properties_map: Mapping[
                tasks.UID, NetworkTaskDrawingProperties
            ],
        ) -> Callable[[tasks.UID], NetworkTaskDrawingProperties]:
            def inner(task: tasks.UID) -> NetworkTaskDrawingProperties:
                if task in intercepted_task_to_properties_map:
                    return intercepted_task_to_properties_map[task]
                return get_task_properties(task)

            return inner

        def wrap_with_relationship_interceptor(
            get_relationship_properties: Callable[
                [tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties
            ],
            intercepted_relationship_to_properties_map: Mapping[
                tuple[tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties
            ],
        ) -> Callable[[tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties]:
            def inner(
                source: tasks.UID, target: tasks.UID
            ) -> NetworkRelationshipDrawingProperties:
                if (source, target) in intercepted_relationship_to_properties_map:
                    return intercepted_relationship_to_properties_map[(source, target)]
                return get_relationship_properties(source, target)

            return inner

        def wrap_relationship_map_as_function(
            relationship_to_properties_map: Mapping[
                tuple[tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties
            ],
        ) -> Callable[[tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties]:
            def inner(
                source: tasks.UID, target: tasks.UID
            ) -> NetworkRelationshipDrawingProperties:
                return relationship_to_properties_map[(source, target)]

            return inner

        super().__init__(master=master)

        legend_elements = list(legend_elements) if legend_elements is not None else []

        if highlighted_task_groups:
            highlighted_task_to_properties_map = dict[
                tasks.UID, NetworkTaskDrawingProperties
            ]()
            for label, properties, task_group in highlighted_task_groups:
                if label is not None:
                    legend_elements.append((label, properties))
                for task in task_group:
                    highlighted_task_to_properties_map[task] = properties
            get_task_properties_ = wrap_with_task_interceptor(
                get_task_properties=get_task_properties,
                intercepted_task_to_properties_map=highlighted_task_to_properties_map,
            )
        else:
            get_task_properties_ = get_task_properties

        if highlighted_hierarchy_groups:
            highlighted_hierarchy_to_properties_map = dict[
                tuple[tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties
            ]()
            for label, properties, hierarchy_group in highlighted_hierarchy_groups:
                if label is not None:
                    legend_elements.append((label, properties))
                for dependee_task, dependent_task in hierarchy_group:
                    highlighted_hierarchy_to_properties_map[
                        (dependee_task, dependent_task)
                    ] = properties
            get_hierarchy_properties_ = wrap_with_relationship_interceptor(
                get_relationship_properties=get_hierarchy_properties,
                intercepted_relationship_to_properties_map=highlighted_hierarchy_to_properties_map,
            )
        else:
            get_hierarchy_properties_ = get_hierarchy_properties

        if highlighted_dependency_groups:
            highlighted_dependency_to_properties_map = dict[
                tuple[tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties
            ]()
            for label, properties, dependency_group in highlighted_dependency_groups:
                if label is not None:
                    legend_elements.append((label, properties))
                for source, target in dependency_group:
                    highlighted_dependency_to_properties_map[(source, target)] = (
                        properties
                    )
            get_dependency_properties_ = wrap_with_relationship_interceptor(
                get_relationship_properties=get_dependency_properties,
                intercepted_relationship_to_properties_map=highlighted_dependency_to_properties_map,
            )
        else:
            get_dependency_properties_ = get_dependency_properties

        if additional_hierarchy_groups:
            additional_hierarchies_ = set[tuple[tasks.UID, tasks.UID]]()
            additional_hierarchy_to_properties_map = dict[
                tuple[tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties
            ]()
            for label, properties, hierarchy_group in additional_hierarchy_groups:
                if label is not None:
                    legend_elements.append((label, properties))
                for dependee_task, dependent_task in hierarchy_group:
                    additional_hierarchies_.add((dependee_task, dependent_task))
                    additional_hierarchy_to_properties_map[
                        (dependee_task, dependent_task)
                    ] = properties
            additional_hierarchies = AdditionalRelationships(
                relationships=additional_hierarchies_,
                get_relationship_properties=wrap_relationship_map_as_function(
                    relationship_to_properties_map=additional_hierarchy_to_properties_map
                ),
            )
        else:
            additional_hierarchies = None

        if additional_dependency_groups:
            additional_dependencies_ = set[tuple[tasks.UID, tasks.UID]]()
            additional_dependency_to_properties_map = dict[
                tuple[tasks.UID, tasks.UID], NetworkRelationshipDrawingProperties
            ]()
            for label, properties, dependency_group in additional_dependency_groups:
                if label is not None:
                    legend_elements.append((label, properties))
                for dependee_task, dependent_task in dependency_group:
                    additional_dependencies_.add((dependee_task, dependent_task))
                    additional_dependency_to_properties_map[
                        (dependee_task, dependent_task)
                    ] = properties
            additional_dependencies = AdditionalRelationships(
                relationships=additional_dependencies_,
                get_relationship_properties=wrap_relationship_map_as_function(
                    relationship_to_properties_map=additional_dependency_to_properties_map
                ),
            )
        else:
            additional_dependencies = None

        self._description_label = ttk.Label(self, text=description_text)

        self._graph = StaticTaskNetworkGraph(
            master=self,
            graph=task_network,
            get_task_annotation_text=get_task_annotation_text,
            get_task_properties=get_task_properties_,
            get_hierarchy_properties=get_hierarchy_properties_,
            get_dependency_properties=get_dependency_properties_,
            additional_hierarchies=additional_hierarchies,
            additional_dependencies=additional_dependencies,
            legend_elements=legend_elements,
        )

        self._description_label.grid(row=0, column=0)
        self._graph.grid(row=1, column=0)
