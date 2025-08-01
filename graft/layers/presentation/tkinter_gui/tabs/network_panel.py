import enum
import tkinter as tk
from collections.abc import Callable, Iterable
from tkinter import ttk
from typing import Final

from graft import architecture
from graft.domain import tasks
from graft.domain.tasks.network_graph import NetworkGraph, NetworkGraphView
from graft.layers.presentation.tkinter_gui import (
    domain_visual_language,
    event_broker,
    helpers,
)
from graft.layers.presentation.tkinter_gui.domain_visual_language import (
    ACTIVE_COMPOSITE_TASK_COLOUR,
    ACTIVE_CONCRETE_TASK_COLOUR,
    COMPLETED_TASK_COLOUR,
    DOWNSTREAM_TASK_COLOUR,
    HIGH_IMPORTANCE_COLOUR,
    IN_PROGRESS_TASK_COLOUR,
    INACTIVE_TASK_COLOUR,
    LOW_IMPORTANCE_COLOUR,
    MEDIUM_IMPORTANCE_COLOUR,
    NOT_STARTED_TASK_COLOUR,
    get_network_dependency_properties,
    get_network_hierarchy_properties,
    get_network_task_properties,
)
from graft.layers.presentation.tkinter_gui.helpers.colour import RED
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.network_task_drawing_properties import (
    NetworkTaskDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.relationship_drawing_properties import (
    NetworkRelationshipDrawingProperties,
)

_FILTER_OPTION_COMPONENT: Final = "component"
_FILTER_OPTION_SUBGRAPH: Final = "subgraph"
_FILTER_OPTION_SUPERGRAPH: Final = "supergraph"
_FILTER_OPTION_DOWNSTREAM: Final = "downstream"
_FILTER_OPTION_UPSTREAM: Final = "upstream"
_FILTER_OPTION_NONE = "none"

_COLOURING_OPTION_STANDARD: Final = "standard"
_COLOURING_OPTION_IMPORTANCE: Final = "importance"
_COLOURING_OPTION_PROGRESS: Final = "progress"
_COLOURING_OPTION_ACTIVE: Final = "active"

_SELECTED_ALPHA_LEVEL: Final = domain_visual_language.NetworkAlphaLevel.VERY_HIGHLIGHTED

# Standard colouring
_STANDARD_TASK_DRAWING_PROPERTIES: Final = get_network_task_properties()
_STANDARD_SELECTED_TASK_DRAWING_PROPERTIES: Final = get_network_task_properties(
    colour=RED, alpha_level=_SELECTED_ALPHA_LEVEL
)
_STANDARD_HIERARCHY_DRAWING_PROPERTIES: Final = get_network_hierarchy_properties()
_STANDARD_SELECTED_HIERARCHY_PROPERTIES: Final = get_network_hierarchy_properties(
    alpha_level=_SELECTED_ALPHA_LEVEL
)
_STANDARD_DEPENDENCY_DRAWING_PROPERTIES: Final = get_network_dependency_properties()
_STANDARD_SELECTED_DEPENDENCY_PROPERTIES: Final = get_network_dependency_properties(
    alpha_level=_SELECTED_ALPHA_LEVEL
)

# Importance colouring
_IMPORTANCE_HIGH_TASK_DRAWING_PROPERTIES: Final = get_network_task_properties(
    colour=HIGH_IMPORTANCE_COLOUR
)
_IMPORTANCE_HIGH_SELECTED_TASK_DRAWING_PROPERTIES: Final = get_network_task_properties(
    colour=HIGH_IMPORTANCE_COLOUR, alpha_level=_SELECTED_ALPHA_LEVEL
)
_IMPORTANCE_MEDIUM_TASK_DRAWING_PROPERTIES: Final = get_network_task_properties(
    colour=MEDIUM_IMPORTANCE_COLOUR
)
_IMPORTANCE_MEDIUM_SELECTED_TASK_DRAWING_PROPERTIES: Final = (
    get_network_task_properties(
        colour=MEDIUM_IMPORTANCE_COLOUR, alpha_level=_SELECTED_ALPHA_LEVEL
    )
)
_IMPORTANCE_LOW_TASK_DRAWING_PROPERTIES: Final = get_network_task_properties(
    colour=LOW_IMPORTANCE_COLOUR
)
_IMPORTANCE_LOW_SELECTED_TASK_DRAWING_PROPERTIES: Final = get_network_task_properties(
    colour=LOW_IMPORTANCE_COLOUR, alpha_level=_SELECTED_ALPHA_LEVEL
)
_IMPORTANCE_NONE_TASK_DRAWING_PROPERTIES: Final = get_network_task_properties()
_IMPORTANCE_NONE_SELECTED_TASK_DRAWING_PROPERTIES: Final = get_network_task_properties(
    alpha_level=_SELECTED_ALPHA_LEVEL
)
_IMPORTANCE_HIERARCHY_DRAWING_PROPERTIES = get_network_hierarchy_properties()
_IMPORTANCE_SELECTED_HIERARCHY_DRAWING_PROPERTIES = get_network_hierarchy_properties(
    alpha_level=_SELECTED_ALPHA_LEVEL
)
_IMPORTANCE_DEPENDENCY_DRAWING_PROPERTIES = get_network_dependency_properties()
_IMPORTANCE_SELECTED_DEPENDENCY_DRAWING_PROPERTIES = get_network_dependency_properties(
    alpha_level=_SELECTED_ALPHA_LEVEL
)

# Progress colouring
_PROGRESS_COMPLETED_TASK_DRAWING_PROPERTIES: Final = get_network_task_properties(
    colour=COMPLETED_TASK_COLOUR
)
_PROGRESS_COMPLETED_SELECTED_TASK_DRAWING_PROPERTIES: Final = (
    get_network_task_properties(
        colour=COMPLETED_TASK_COLOUR, alpha_level=_SELECTED_ALPHA_LEVEL
    )
)
_PROGRESS_IN_PROGRESS_TASK_DRAWING_PROPERTIES: Final = get_network_task_properties(
    colour=IN_PROGRESS_TASK_COLOUR
)
_PROGRESS_IN_PROGRESS_SELECTED_TASK_DRAWING_PROPERTIES: Final = (
    get_network_task_properties(
        colour=IN_PROGRESS_TASK_COLOUR, alpha_level=_SELECTED_ALPHA_LEVEL
    )
)
_PROGRESS_NOT_STARTED_TASK_DRAWING_PROPERTIES: Final = get_network_task_properties(
    colour=NOT_STARTED_TASK_COLOUR
)
_PROGRESS_NOT_STARTED_SELECTED_TASK_DRAWING_PROPERTIES: Final = (
    get_network_task_properties(
        colour=NOT_STARTED_TASK_COLOUR, alpha_level=_SELECTED_ALPHA_LEVEL
    )
)
_PROGRESS_HIERARCHY_DRAWING_PROPERTIES: Final = get_network_hierarchy_properties()
_PROGRESS_SELECTED_HIERARCHY_DRAWING_PROPERTIES: Final = (
    get_network_hierarchy_properties(alpha_level=_SELECTED_ALPHA_LEVEL)
)
_PROGRESS_DEPENDENCY_DRAWING_PROPERTIES: Final = get_network_dependency_properties()
_PROGRESS_SELECTED_DEPENDENCY_DRAWING_PROPERTIES: Final = (
    get_network_dependency_properties(alpha_level=_SELECTED_ALPHA_LEVEL)
)


# Active colouring
_ACTIVE_ACTIVE_CONCRETE_TASK_DRAWING_PROPERTIES: Final = get_network_task_properties(
    colour=ACTIVE_CONCRETE_TASK_COLOUR
)
_ACTIVE_ACTIVE_CONCRETE_SELECTED_TASK_DRAWING_PROPERTIES = get_network_task_properties(
    colour=ACTIVE_CONCRETE_TASK_COLOUR, alpha_level=_SELECTED_ALPHA_LEVEL
)
_ACTIVE_ACTIVE_COMPOSITE_TASK_DRAWING_PROPERTIES: Final = get_network_task_properties(
    colour=ACTIVE_COMPOSITE_TASK_COLOUR,
    alpha_level=domain_visual_language.NetworkAlphaLevel.FADED,
)
_ACTIVE_ACTIVE_COMPOSITE_SELECTED_TASK_DRAWING_PROPERTIES = get_network_task_properties(
    colour=ACTIVE_COMPOSITE_TASK_COLOUR, alpha_level=_SELECTED_ALPHA_LEVEL
)
_ACTIVE_INACTIVE_DOWNSTREAM_TASK_DRAWING_PROPERTIES = get_network_task_properties(
    colour=DOWNSTREAM_TASK_COLOUR,
    alpha_level=domain_visual_language.NetworkAlphaLevel.FADED,
)
_ACTIVE_INACTIVE_DOWNSTREAM_SELECTED_TASK_DRAWING_PROPERTIES = (
    get_network_task_properties(
        colour=DOWNSTREAM_TASK_COLOUR,
        alpha_level=_SELECTED_ALPHA_LEVEL,
    )
)
_ACTIVE_COMPLETED_TASK_DRAWING_PROPERTIES: Final = get_network_task_properties(
    colour=INACTIVE_TASK_COLOUR,
    alpha_level=domain_visual_language.NetworkAlphaLevel.VERY_FADED,
)
_ACTIVE_COMPLETED_SELECTED_TASK_DRAWING_PROPERTIES: Final = get_network_task_properties(
    colour=INACTIVE_TASK_COLOUR,
    alpha_level=_SELECTED_ALPHA_LEVEL,
)
_ACTIVE_HIERARCHY_DRAWING_PROPERTIES: Final = get_network_hierarchy_properties()
_ACTIVE_SELECTED_HIERARCHY_DRAWING_PROPERTIES: Final = get_network_hierarchy_properties(
    alpha_level=_SELECTED_ALPHA_LEVEL
)

_ACTIVE_DEPENDENCY_DRAWING_PROPERTIES: Final = get_network_dependency_properties()
_ACTIVE_SELECTED_DEPENDENCY_DRAWING_PROPERTIES: Final = (
    get_network_dependency_properties(alpha_level=_SELECTED_ALPHA_LEVEL)
)

_NO_TASK_FILTER_TASK_MENU_OPTION: Final = ""


class ColouringOption(enum.Enum):
    STANDARD = enum.auto()
    IMPORTANCE = enum.auto()
    PROGRESS = enum.auto()
    ACTIVE = enum.auto()


class FilterOption(enum.Enum):
    COMPONENT = enum.auto()
    SUBGRAPH = enum.auto()
    SUPERGRAPH = enum.auto()
    DOWNSTREAM = enum.auto()
    UPSTREAM = enum.auto()
    NONE = enum.auto()


def _parse_colouring_option(text: str) -> ColouringOption:
    if text == _COLOURING_OPTION_STANDARD:
        return ColouringOption.STANDARD

    if text == _COLOURING_OPTION_IMPORTANCE:
        return ColouringOption.IMPORTANCE

    if text == _COLOURING_OPTION_PROGRESS:
        return ColouringOption.PROGRESS

    if text == _COLOURING_OPTION_ACTIVE:
        return ColouringOption.ACTIVE

    raise ValueError


def _parse_filter_option(text: str) -> FilterOption:
    if text == _FILTER_OPTION_COMPONENT:
        return FilterOption.COMPONENT

    if text == _FILTER_OPTION_SUBGRAPH:
        return FilterOption.SUBGRAPH

    if text == _FILTER_OPTION_SUPERGRAPH:
        return FilterOption.SUPERGRAPH

    if text == _FILTER_OPTION_DOWNSTREAM:
        return FilterOption.DOWNSTREAM

    if text == _FILTER_OPTION_UPSTREAM:
        return FilterOption.UPSTREAM

    if text == _FILTER_OPTION_NONE:
        return FilterOption.NONE

    raise ValueError


def _format_task_uid_name_as_menu_option(
    task_uid: tasks.UID, task_name: tasks.Name
) -> str:
    return f"[{task_uid}] {task_name}" if task_name else f"[{task_uid}]"


def _get_menu_options(
    tasks_: Iterable[tasks.UID], get_task_name: Callable[[tasks.UID], tasks.Name]
) -> list[str]:
    return [
        _NO_TASK_FILTER_TASK_MENU_OPTION,
        *(
            _format_task_uid_name_as_menu_option(task, get_task_name(task))
            for task in sorted(tasks_)
        ),
    ]


def _parse_task_uid_from_menu_option(menu_option: str) -> tasks.UID | None:
    if menu_option == _NO_TASK_FILTER_TASK_MENU_OPTION:
        return None
    first_closing_square_bracket = menu_option.find("]")
    uid_number = int(menu_option[1:first_closing_square_bracket])
    return tasks.UID(uid_number)


def _format_task_name_for_annotation(name: tasks.Name) -> str | None:
    """Helper function to transform a task name into the form expected by annotation text."""
    return str(name) if name else None


def _publish_task_as_selected(task: tasks.UID) -> None:
    broker = event_broker.get_singleton()
    broker.publish(event_broker.TaskSelected(task=task))


class NetworkPanel(ttk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)

        self._logic_layer = logic_layer
        self._selected_task: tasks.UID | None = None

        self._control_panel = ttk.Frame(master=self)

        self._colouring_panel = ttk.Frame(master=self._control_panel)
        self._colouring_label = ttk.Label(
            master=self._colouring_panel, text="Visualisation"
        )
        self._colouring_selection = tk.StringVar(value=_COLOURING_OPTION_STANDARD)
        self._colouring_dropdown = ttk.Combobox(
            self._colouring_panel,
            textvariable=self._colouring_selection,
            values=[
                _COLOURING_OPTION_STANDARD,
                _COLOURING_OPTION_IMPORTANCE,
                _COLOURING_OPTION_PROGRESS,
                _COLOURING_OPTION_ACTIVE,
            ],
            state="readonly",
        )
        self._colouring_dropdown.bind(
            "<<ComboboxSelected>>", lambda _: self._update_figure()
        )

        self._filter_panel = ttk.Frame(master=self._control_panel)

        self._filter_panel_label = ttk.Label(self._filter_panel, text="Filtering")
        self._filter_options_panel = ttk.Frame(master=self._filter_panel)
        self._filter_selection = tk.StringVar(value=_FILTER_OPTION_NONE)
        self._filter_options_dropdown = ttk.Combobox(
            self._filter_options_panel,
            textvariable=self._filter_selection,
            values=[
                _FILTER_OPTION_NONE,
                _FILTER_OPTION_COMPONENT,
                _FILTER_OPTION_SUBGRAPH,
                _FILTER_OPTION_SUPERGRAPH,
                _FILTER_OPTION_DOWNSTREAM,
                _FILTER_OPTION_UPSTREAM,
            ],
            state="readonly",
        )
        self._filter_options_dropdown.bind(
            "<<ComboboxSelected>>", lambda _: self._on_filter_option_selected()
        )
        self._filter_task_selection = tk.StringVar()
        self._filter_task_options_menu = ttk.Combobox(
            self._filter_options_panel,
            textvariable=self._filter_task_selection,
            values=[
                _NO_TASK_FILTER_TASK_MENU_OPTION,
                _NO_TASK_FILTER_TASK_MENU_OPTION,
            ],
            state="disabled",
        )
        self._filter_task_options_menu.bind(
            "<<ComboboxSelected>>", lambda _: self._update_figure()
        )
        self._show_completed_tasks = tk.BooleanVar()
        self._show_completed_tasks_checkbutton = ttk.Checkbutton(
            self._filter_panel,
            text="Show completed tasks",
            variable=self._show_completed_tasks,
            command=self._on_show_completed_tasks_button_toggled,
        )
        self._show_completed_tasks.set(False)

        self._static_graph = helpers.StaticTaskNetworkGraph(
            master=self,
            graph=tasks.NetworkGraph.empty(),
            get_task_annotation_text=self._get_formatted_task_name,
            get_task_properties=self._get_task_properties,
            get_hierarchy_properties=self._get_hierarchy_properties,
            get_dependency_properties=self._get_dependency_properties,
            additional_hierarchies=None,
            additional_dependencies=None,
            on_node_left_click=_publish_task_as_selected,
        )

        self._control_panel.grid(row=0, column=0)
        self._colouring_panel.grid(row=0, column=0)
        self._colouring_label.grid(row=0, column=0)
        self._colouring_dropdown.grid(row=1, column=0)
        self._filter_panel.grid(row=0, column=1)
        self._filter_panel_label.grid(row=0, column=0)
        self._filter_options_panel.grid(row=1, column=0)
        self._filter_options_dropdown.grid(row=0, column=0)
        self._filter_task_options_menu.grid(row=1, column=0)
        self._show_completed_tasks_checkbutton.grid(row=2, column=0)

        self._static_graph.grid(row=1, column=0)

        self._update_filter_task_menu_options()
        self._update_figure()

        broker = event_broker.get_singleton()
        broker.subscribe(event_broker.SystemModified, self._on_system_modified)
        broker.subscribe(event_broker.TaskSelected, self._on_task_selected)

    def _on_filter_option_selected(self) -> None:
        self._filter_task_options_menu["state"] = (
            "disabled"
            if self._get_selected_filter() is FilterOption.NONE
            else "readonly"
        )
        self._update_figure()

    def _get_task_to_filter_on(self) -> tasks.UID | None:
        return _parse_task_uid_from_menu_option(self._filter_task_selection.get())

    def _on_system_modified(self, event: event_broker.Event) -> None:
        if not isinstance(event, event_broker.SystemModified):
            raise TypeError

        if (
            self._selected_task is not None
            and self._selected_task not in self._logic_layer.get_task_system().tasks()
        ):
            self._selected_task = None

        if (
            self._get_task_to_filter_on() is not None
            and self._get_task_to_filter_on()
            not in self._logic_layer.get_task_system().tasks()
        ):
            self._filter_task_selection.set("")

        self._update_filter_task_menu_options()

        self._update_figure()

    def _on_task_selected(self, event: event_broker.Event) -> None:
        if not isinstance(event, event_broker.TaskSelected):
            raise TypeError

        if self._selected_task is not None and event.task == self._selected_task:
            return

        self._selected_task = event.task
        self._update_figure()

    def _get_formatted_task_name(self, task: tasks.UID) -> str | None:
        name = self._logic_layer.get_task_system().attributes_register()[task].name
        return _format_task_name_for_annotation(name)

    def _publish_task_as_selected(self, task: tasks.UID) -> None:
        broker = event_broker.get_singleton()
        broker.publish(event_broker.TaskSelected(task=task))

    def _get_hierarchy_properties(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> NetworkRelationshipDrawingProperties:
        match self._get_selected_colouring():
            case ColouringOption.STANDARD:
                return self._get_standard_hierarchy_properties(supertask, subtask)
            case ColouringOption.IMPORTANCE:
                return self._get_importance_hierarchy_properties(supertask, subtask)
            case ColouringOption.PROGRESS:
                return self._get_progress_hierarchy_properties(supertask, subtask)
            case ColouringOption.ACTIVE:
                return self._get_active_hierarchy_properties(supertask, subtask)
            case _:
                raise ValueError

    def _get_dependency_properties(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> NetworkRelationshipDrawingProperties:
        match self._get_selected_colouring():
            case ColouringOption.STANDARD:
                return self._get_standard_dependency_properties(
                    dependee_task, dependent_task
                )
            case ColouringOption.IMPORTANCE:
                return self._get_importance_dependency_properties(
                    dependee_task, dependent_task
                )
            case ColouringOption.PROGRESS:
                return self._get_progress_dependency_properties(
                    dependee_task, dependent_task
                )
            case ColouringOption.ACTIVE:
                return self._get_active_dependency_properties(
                    dependee_task, dependent_task
                )
            case _:
                raise ValueError

    def _get_task_properties(self, task: tasks.UID) -> NetworkTaskDrawingProperties:
        match self._get_selected_colouring():
            case ColouringOption.STANDARD:
                return self._get_standard_task_properties(task)
            case ColouringOption.IMPORTANCE:
                return self._get_importance_task_properties(task)
            case ColouringOption.PROGRESS:
                return self._get_progress_task_properties(task)
            case ColouringOption.ACTIVE:
                return self._get_active_task_properties(task)
            case _:
                raise ValueError

    def _get_selected_colouring(self) -> ColouringOption:
        return _parse_colouring_option(self._colouring_selection.get())

    def _get_standard_task_properties(
        self, task: tasks.UID
    ) -> NetworkTaskDrawingProperties:
        return (
            _STANDARD_SELECTED_TASK_DRAWING_PROPERTIES
            if task == self._selected_task
            else _STANDARD_TASK_DRAWING_PROPERTIES
        )

    def _get_standard_hierarchy_properties(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> NetworkRelationshipDrawingProperties:
        return (
            _STANDARD_SELECTED_HIERARCHY_PROPERTIES
            if self._selected_task in {supertask, subtask}
            else _STANDARD_HIERARCHY_DRAWING_PROPERTIES
        )

    def _get_standard_dependency_properties(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> NetworkRelationshipDrawingProperties:
        return (
            _STANDARD_SELECTED_DEPENDENCY_PROPERTIES
            if self._selected_task in {dependee_task, dependent_task}
            else _STANDARD_DEPENDENCY_DRAWING_PROPERTIES
        )

    def _get_importance_task_properties(
        self, task: tasks.UID
    ) -> NetworkTaskDrawingProperties:
        match self._logic_layer.get_task_system().get_importance(task):
            case tasks.Importance.LOW:
                return (
                    _IMPORTANCE_LOW_SELECTED_TASK_DRAWING_PROPERTIES
                    if task == self._selected_task
                    else _IMPORTANCE_LOW_TASK_DRAWING_PROPERTIES
                )
            case tasks.Importance.MEDIUM:
                return (
                    _IMPORTANCE_MEDIUM_SELECTED_TASK_DRAWING_PROPERTIES
                    if task == self._selected_task
                    else _IMPORTANCE_MEDIUM_TASK_DRAWING_PROPERTIES
                )
            case tasks.Importance.HIGH:
                return (
                    _IMPORTANCE_HIGH_SELECTED_TASK_DRAWING_PROPERTIES
                    if task == self._selected_task
                    else _IMPORTANCE_HIGH_TASK_DRAWING_PROPERTIES
                )
            case None:
                return (
                    _IMPORTANCE_NONE_SELECTED_TASK_DRAWING_PROPERTIES
                    if task == self._selected_task
                    else _IMPORTANCE_NONE_TASK_DRAWING_PROPERTIES
                )

    def _get_importance_hierarchy_properties(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> NetworkRelationshipDrawingProperties:
        return (
            _IMPORTANCE_SELECTED_HIERARCHY_DRAWING_PROPERTIES
            if self._selected_task in {supertask, subtask}
            else _IMPORTANCE_HIERARCHY_DRAWING_PROPERTIES
        )

    def _get_importance_dependency_properties(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> NetworkRelationshipDrawingProperties:
        return (
            _IMPORTANCE_SELECTED_DEPENDENCY_DRAWING_PROPERTIES
            if self._selected_task in {dependee_task, dependent_task}
            else _IMPORTANCE_DEPENDENCY_DRAWING_PROPERTIES
        )

    def _get_progress_task_properties(
        self, task: tasks.UID
    ) -> NetworkTaskDrawingProperties:
        match self._logic_layer.get_task_system().get_progress(task):
            case tasks.Progress.NOT_STARTED:
                return (
                    _PROGRESS_NOT_STARTED_SELECTED_TASK_DRAWING_PROPERTIES
                    if task == self._selected_task
                    else _PROGRESS_NOT_STARTED_TASK_DRAWING_PROPERTIES
                )
            case tasks.Progress.IN_PROGRESS:
                return (
                    _PROGRESS_IN_PROGRESS_SELECTED_TASK_DRAWING_PROPERTIES
                    if task == self._selected_task
                    else _PROGRESS_IN_PROGRESS_TASK_DRAWING_PROPERTIES
                )
            case tasks.Progress.COMPLETED:
                return (
                    _PROGRESS_COMPLETED_SELECTED_TASK_DRAWING_PROPERTIES
                    if task == self._selected_task
                    else _PROGRESS_COMPLETED_TASK_DRAWING_PROPERTIES
                )

    def _get_progress_hierarchy_properties(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> NetworkRelationshipDrawingProperties:
        return (
            _PROGRESS_SELECTED_HIERARCHY_DRAWING_PROPERTIES
            if self._selected_task in {supertask, subtask}
            else _PROGRESS_HIERARCHY_DRAWING_PROPERTIES
        )

    def _get_progress_dependency_properties(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> NetworkRelationshipDrawingProperties:
        return (
            _PROGRESS_SELECTED_DEPENDENCY_DRAWING_PROPERTIES
            if self._selected_task in {dependee_task, dependent_task}
            else _PROGRESS_DEPENDENCY_DRAWING_PROPERTIES
        )

    def _get_active_task_properties(
        self, task: tasks.UID
    ) -> NetworkTaskDrawingProperties:
        if task == self._selected_task:
            if self._logic_layer.get_task_system().is_active_task(task):
                return (
                    _ACTIVE_ACTIVE_CONCRETE_SELECTED_TASK_DRAWING_PROPERTIES
                    if (
                        self._logic_layer.get_task_system()
                        .network_graph()
                        .hierarchy_graph()
                        .is_concrete(task)
                    )
                    else _ACTIVE_ACTIVE_COMPOSITE_SELECTED_TASK_DRAWING_PROPERTIES
                )
            if (
                self._logic_layer.get_task_system().get_progress(task)
                is tasks.Progress.NOT_STARTED
            ):
                return _ACTIVE_INACTIVE_DOWNSTREAM_SELECTED_TASK_DRAWING_PROPERTIES
            return _ACTIVE_COMPLETED_SELECTED_TASK_DRAWING_PROPERTIES
        if self._logic_layer.get_task_system().is_active_task(task):
            return (
                _ACTIVE_ACTIVE_CONCRETE_TASK_DRAWING_PROPERTIES
                if (
                    self._logic_layer.get_task_system()
                    .network_graph()
                    .hierarchy_graph()
                    .is_concrete(task)
                )
                else _ACTIVE_ACTIVE_COMPOSITE_TASK_DRAWING_PROPERTIES
            )
        if (
            self._logic_layer.get_task_system().get_progress(task)
            is tasks.Progress.NOT_STARTED
        ):
            return _ACTIVE_INACTIVE_DOWNSTREAM_TASK_DRAWING_PROPERTIES
        return _ACTIVE_COMPLETED_TASK_DRAWING_PROPERTIES

    def _get_active_hierarchy_properties(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> NetworkRelationshipDrawingProperties:
        return (
            _ACTIVE_SELECTED_HIERARCHY_DRAWING_PROPERTIES
            if self._selected_task in {supertask, subtask}
            else _ACTIVE_HIERARCHY_DRAWING_PROPERTIES
        )

    def _get_active_dependency_properties(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> NetworkRelationshipDrawingProperties:
        return (
            _ACTIVE_SELECTED_DEPENDENCY_DRAWING_PROPERTIES
            if self._selected_task in {dependee_task, dependent_task}
            else _ACTIVE_DEPENDENCY_DRAWING_PROPERTIES
        )

    def _get_filtered_graph(self) -> NetworkGraphView:
        system = self._logic_layer.get_task_system()
        # Need to check the system isn't empty of this will break
        if system and not self._show_completed_tasks.get():
            system = tasks.get_incomplete_system(system)

        # Need to check the system isn't empty of this will break
        if system and (filter_task := self._get_task_to_filter_on()) is not None:
            if filter_task in system.tasks():
                match self._get_selected_filter():
                    case FilterOption.COMPONENT:
                        subgraph = NetworkGraphView(
                            system.network_graph().component_subgraph(filter_task)
                        )
                    case FilterOption.SUBGRAPH:
                        subgraph = NetworkGraphView(
                            tasks.get_inferior_subgraph(
                                filter_task, system.network_graph()
                            )
                        )
                    case FilterOption.SUPERGRAPH:
                        subgraph = NetworkGraphView(
                            tasks.get_superior_subgraph(
                                filter_task, system.network_graph()
                            )
                        )
                    case FilterOption.DOWNSTREAM:
                        subgraph = NetworkGraphView(
                            system.network_graph().downstream_subgraph([filter_task])
                        )
                    case FilterOption.UPSTREAM:
                        subgraph = NetworkGraphView(
                            system.network_graph().upstream_subgraph([filter_task])
                        )
                    case FilterOption.NONE:
                        subgraph = system.network_graph()
            else:
                subgraph = NetworkGraphView(NetworkGraph.empty())
        else:
            subgraph = system.network_graph()

        return subgraph

    def _get_selected_filter(self) -> FilterOption:
        return _parse_filter_option(self._filter_selection.get())

    def _get_legend_elements(
        self,
    ) -> list[
        tuple[str, NetworkTaskDrawingProperties | NetworkRelationshipDrawingProperties]
    ]:
        match self._get_selected_colouring():
            case ColouringOption.STANDARD:
                return [
                    ("task", _STANDARD_TASK_DRAWING_PROPERTIES),
                    ("selected task", _STANDARD_SELECTED_TASK_DRAWING_PROPERTIES),
                    ("hierarchy", _STANDARD_SELECTED_HIERARCHY_PROPERTIES),
                    ("dependency", _STANDARD_SELECTED_DEPENDENCY_PROPERTIES),
                ]
            case ColouringOption.IMPORTANCE:
                return [
                    (
                        "high importance",
                        _IMPORTANCE_HIGH_SELECTED_TASK_DRAWING_PROPERTIES,
                    ),
                    (
                        "medium importance",
                        _IMPORTANCE_MEDIUM_SELECTED_TASK_DRAWING_PROPERTIES,
                    ),
                    (
                        "low importance",
                        _IMPORTANCE_LOW_SELECTED_TASK_DRAWING_PROPERTIES,
                    ),
                    (
                        "no importance",
                        _IMPORTANCE_NONE_SELECTED_TASK_DRAWING_PROPERTIES,
                    ),
                    ("hierarchy", _IMPORTANCE_SELECTED_HIERARCHY_DRAWING_PROPERTIES),
                    ("dependency", _IMPORTANCE_SELECTED_DEPENDENCY_DRAWING_PROPERTIES),
                ]
            case ColouringOption.PROGRESS:
                return [
                    (
                        "not started",
                        _PROGRESS_NOT_STARTED_SELECTED_TASK_DRAWING_PROPERTIES,
                    ),
                    (
                        "in progress",
                        _PROGRESS_IN_PROGRESS_SELECTED_TASK_DRAWING_PROPERTIES,
                    ),
                    ("completed", _PROGRESS_COMPLETED_SELECTED_TASK_DRAWING_PROPERTIES),
                    ("hierarchy", _PROGRESS_SELECTED_HIERARCHY_DRAWING_PROPERTIES),
                    ("dependency", _PROGRESS_SELECTED_DEPENDENCY_DRAWING_PROPERTIES),
                ]
            case ColouringOption.ACTIVE:
                return [
                    (
                        "active (concrete)",
                        _ACTIVE_ACTIVE_CONCRETE_SELECTED_TASK_DRAWING_PROPERTIES,
                    ),
                    (
                        "active (composite)",
                        _ACTIVE_ACTIVE_COMPOSITE_SELECTED_TASK_DRAWING_PROPERTIES,
                    ),
                    (
                        "downstream",
                        _ACTIVE_INACTIVE_DOWNSTREAM_TASK_DRAWING_PROPERTIES,
                    ),
                    ("completed", _ACTIVE_COMPLETED_TASK_DRAWING_PROPERTIES),
                    ("hierarchy", _ACTIVE_SELECTED_HIERARCHY_DRAWING_PROPERTIES),
                    ("dependency", _ACTIVE_SELECTED_DEPENDENCY_DRAWING_PROPERTIES),
                ]

    def _update_figure(self) -> None:
        self._static_graph.update_graph(
            self._get_filtered_graph(), legend_elements=self._get_legend_elements()
        )

    def _update_filter_task_menu_options(self) -> None:
        system = (
            self._logic_layer.get_task_system()
            if self._show_completed_tasks.get()
            else tasks.get_incomplete_system(self._logic_layer.get_task_system())
        )
        menu_options = _get_menu_options(
            system.tasks(),
            get_task_name=lambda task: self._logic_layer.get_task_system()
            .attributes_register()[task]
            .name,
        )
        self._filter_task_options_menu["values"] = menu_options
        if self._get_task_to_filter_on() not in system.tasks():
            self._filter_task_selection.set(_NO_TASK_FILTER_TASK_MENU_OPTION)

    def _on_show_completed_tasks_button_toggled(self) -> None:
        self._update_filter_task_menu_options()
        self._update_figure()
