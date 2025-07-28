import enum
import tkinter as tk
from collections.abc import Generator
from tkinter import ttk
from typing import Final

from graft import architecture
from graft.domain import tasks
from graft.domain.tasks.graph_processing import (
    get_component_system,
    get_inferior_subsystem,
)
from graft.domain.tasks.network_graph import NetworkGraphView
from graft.layers.presentation.tkinter_gui import event_broker, helpers
from graft.layers.presentation.tkinter_gui.helpers.alpha import OPAQUE, Alpha
from graft.layers.presentation.tkinter_gui.helpers.colour import (
    BLUE,
    GREEN,
    GREY,
    LIGHT_BLUE,
    LIGHT_YELLOW,
    ORANGE,
    RED,
    YELLOW,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.relationship_drawing_properties import (
    RelationshipDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.static_task_network_graph import (
    DEFAULT_STANDARD_DEPENDENCY_COLOUR,
    DEFAULT_STANDARD_HIERARCHY_COLOUR,
    DEFAULT_STANDARD_RELATIONSHIP_ALPHA,
    DEFAULT_TASK_ALPHA,
    DEFAULT_TASK_LABEL_COLOUR,
)
from graft.layers.presentation.tkinter_gui.helpers.static_task_network_graph.task_drawing_properties import (
    TaskDrawingProperties,
)

_FILTER_OPTION_COMPONENT: Final = "component"
_FILTER_OPTION_SINGLE_TASK: Final = "single task"
_FILTER_OPTION_NONE = "none"

_COLOURING_OPTION_STANDARD: Final = "standard"
_COLOURING_OPTION_IMPORTANCE: Final = "importance"
_COLOURING_OPTION_PROGRESS: Final = "progress"
_COLOURING_OPTION_ACTIVE: Final = "active"

# Standard colouring
_STANDARD_TASK_COLOUR: Final = BLUE
_STANDARD_TASK_ALPHA: Final = DEFAULT_TASK_ALPHA
_STANDARD_SELECTED_TASK_COLOUR: Final = RED
_STANDARD_SELECTED_TASK_ALPHA: Final = OPAQUE
_STANDARD_HIERARCHY_COLOUR: Final = DEFAULT_STANDARD_HIERARCHY_COLOUR
_STANDARD_HIERARCHY_ALPHA: Final = DEFAULT_STANDARD_RELATIONSHIP_ALPHA
_STANDARD_DEPENDENCY_COLOUR: Final = DEFAULT_STANDARD_DEPENDENCY_COLOUR
_STANDARD_DEPENDENCY_ALPHA: Final = DEFAULT_STANDARD_RELATIONSHIP_ALPHA
_STANDARD_SELECTED_HIERARCHY_COLOUR: Final = DEFAULT_STANDARD_HIERARCHY_COLOUR
_STANDARD_SELECTED_HIERARCHY_ALPHA: Final = OPAQUE
_STANDARD_SELECTED_DEPENDENCY_COLOUR: Final = DEFAULT_STANDARD_DEPENDENCY_COLOUR
_STANDARD_SELECTED_DEPENDENCY_ALPHA: Final = OPAQUE

# Importance colouring
_IMPORTANCE_HIGH_TASK_COLOUR: Final = RED
_IMPORTANCE_HIGH_TASK_ALPHA: Final = DEFAULT_TASK_ALPHA
_IMPORTANCE_MEDIUM_TASK_COLOUR: Final = ORANGE
_IMPORTANCE_MEDIUM_TASK_ALPHA: Final = DEFAULT_TASK_ALPHA
_IMPORTANCE_LOW_TASK_COLOUR: Final = YELLOW
_IMPORTANCE_LOW_TASK_ALPHA: Final = DEFAULT_TASK_ALPHA
_IMPORTANCE_NONE_TASK_COLOUR: Final = BLUE
_IMPORTANCE_NONE_TASK_ALPA: Final = DEFAULT_TASK_ALPHA
_IMPORTANCE_HIGH_SELECTED_TASK_COLOUR: Final = RED
_IMPORTANCE_HIGH_SELECTED_TASK_ALPHA: Final = OPAQUE
_IMPORTANCE_MEDIUM_SELECTED_TASK_COLOUR: Final = ORANGE
_IMPORTANCE_MEDIUM_SELECTED_TASK_ALPHA: Final = OPAQUE
_IMPORTANCE_LOW_SELECTED_TASK_COLOUR: Final = YELLOW
_IMPORTANCE_LOW_SELECTED_TASK_ALPHA: Final = OPAQUE
_IMPORTANCE_NONE_SELECTED_TASK_COLOUR: Final = BLUE
_IMPORTANCE_NONE_SELECTED_TASK_ALPHA: Final = OPAQUE
_IMPORTANCE_HIERARCHY_COLOUR: Final = DEFAULT_STANDARD_HIERARCHY_COLOUR
_IMPORTANCE_HIERARCHY_ALPHA: Final = DEFAULT_STANDARD_RELATIONSHIP_ALPHA
_IMPORTANCE_DEPENDENCY_COLOUR: Final = DEFAULT_STANDARD_DEPENDENCY_COLOUR
_IMPORTANCE_DEPENDENCY_ALPHA: Final = DEFAULT_STANDARD_RELATIONSHIP_ALPHA
_IMPORTANCE_SELECTED_HIERARCHY_COLOUR: Final = DEFAULT_STANDARD_HIERARCHY_COLOUR
_IMPORTANCE_SELECTED_HIERARCHY_ALPHA: Final = OPAQUE
_IMPORTANCE_SELECTED_DEPENDENCY_COLOUR: Final = DEFAULT_STANDARD_DEPENDENCY_COLOUR
_IMPORTANCE_SELECTED_DEPENDENCY_ALPHA: Final = OPAQUE

# Progress colouring
_PROGRESS_COMPLETED_TASK_COLOUR: Final = GREEN
_PROGRESS_COMPLETED_TASK_ALPHA: Final = DEFAULT_TASK_ALPHA
_PROGRESS_IN_PROGRESS_TASK_COLOUR: Final = YELLOW
_PROGRESS_IN_PROGRESS_TASK_ALPHA: Final = DEFAULT_TASK_ALPHA
_PROGRESS_NOT_STARTED_TASK_COLOUR: Final = BLUE
_PROGRESS_NOT_STARTED_TASK_ALPHA: Final = DEFAULT_TASK_ALPHA
_PROGRESS_COMPLETED_SELECTED_TASK_COLOUR: Final = GREEN
_PROGRESS_COMPLETED_SELECTED_TASK_ALPHA: Final = OPAQUE
_PROGRESS_IN_PROGRESS_SELECTED_TASK_COLOUR: Final = YELLOW
_PROGRESS_IN_PROGRESS_SELECTED_TASK_ALPHA: Final = OPAQUE
_PROGRESS_NOT_STARTED_SELECTED_TASK_COLOUR: Final = BLUE
_PROGRESS_NOT_STARTED_SELECTED_TASK_ALPHA: Final = OPAQUE
_PROGRESS_HIERARCHY_COLOUR: Final = DEFAULT_STANDARD_HIERARCHY_COLOUR
_PROGRESS_HIERARCHY_ALPHA: Final = DEFAULT_STANDARD_RELATIONSHIP_ALPHA
_PROGRESS_DEPENDENCY_COLOUR: Final = DEFAULT_STANDARD_DEPENDENCY_COLOUR
_PROGRESS_DEPENDENCY_ALPHA: Final = DEFAULT_STANDARD_RELATIONSHIP_ALPHA
_PROGRESS_SELECTED_HIERARCHY_COLOUR: Final = DEFAULT_STANDARD_HIERARCHY_COLOUR
_PROGRESS_SELECTED_HIERARCHY_ALPHA: Final = OPAQUE
_PROGRESS_SELECTED_DEPENDENCY_COLOUR: Final = DEFAULT_STANDARD_DEPENDENCY_COLOUR
_PROGRESS_SELECTED_DEPENDENCY_ALPHA: Final = OPAQUE

# Active colouring
_ACTIVE_ACTIVE_CONCRETE_TASK_COLOUR: Final = YELLOW
_ACTIVE_ACTIVE_CONCRETE_TASK_ALPHA: Final = Alpha(0.9)
_ACTIVE_ACTIVE_NON_CONCRETE_TASK_COLOUR: Final = LIGHT_YELLOW
_ACTIVE_ACTIVE_NON_CONCRETE_TASK_ALPHA: Final = Alpha(0.8)
_ACTIVE_INACTIVE_DOWNSTREAM_TASK_COLOUR: Final = LIGHT_BLUE
_ACTIVE_INACTIVE_DOWNSTREAM_TASK_ALPHA: Final = Alpha(0.7)
_ACTIVE_COMPLETED_TASK_COLOUR: Final = GREY
_ACTIVE_COMPLETED_TASK_ALPHA: Final = Alpha(0.7)
_ACTIVE_ACTIVE_CONCRETE_SELECTED_TASK_COLOUR: Final = YELLOW
_ACTIVE_ACTIVE_CONCRETE_SELECTED_TASK_ALPHA: Final = OPAQUE
_ACTIVE_ACTIVE_NON_CONCRETE_SELECTED_TASK_COLOUR: Final = LIGHT_YELLOW
_ACTIVE_ACTIVE_NON_CONCRETE_SELECTED_TASK_ALPHA: Final = OPAQUE
_ACTIVE_INACTIVE_DOWNSTREAM_SELECTED_TASK_COLOUR: Final = LIGHT_BLUE
_ACTIVE_INACTIVE_DOWNSTREAM_SELECTED_TASK_ALPHA: Final = OPAQUE
_ACTIVE_COMPLETED_SELECTED_TASK_COLOUR: Final = GREY
_ACTIVE_COMPLETED_SELECTED_TASK_ALPHA: Final = OPAQUE
_ACTIVE_HIERARCHY_COLOUR: Final = DEFAULT_STANDARD_HIERARCHY_COLOUR
_ACTIVE_HIERARCHY_ALPHA: Final = DEFAULT_STANDARD_RELATIONSHIP_ALPHA
_ACTIVE_DEPENDENCY_COLOUR: Final = DEFAULT_STANDARD_DEPENDENCY_COLOUR
_ACTIVE_DEPENDENCY_ALPHA: Final = DEFAULT_STANDARD_RELATIONSHIP_ALPHA
_ACTIVE_SELECTED_HIERARCHY_COLOUR: Final = DEFAULT_STANDARD_HIERARCHY_COLOUR
_ACTIVE_SELECTED_HIERARCHY_ALPHA: Final = OPAQUE
_ACTIVE_SELECTED_DEPENDENCY_COLOUR: Final = DEFAULT_STANDARD_DEPENDENCY_COLOUR
_ACTIVE_SELECTED_DEPENDENCY_ALPHA: Final = OPAQUE


class ColouringOption(enum.Enum):
    STANDARD = enum.auto()
    IMPORTANCE = enum.auto()
    PROGRESS = enum.auto()
    ACTIVE = enum.auto()


class FilterOption(enum.Enum):
    COMPONENT = enum.auto()
    SINGLE_TASK = enum.auto()
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

    if text == _FILTER_OPTION_SINGLE_TASK:
        return FilterOption.SINGLE_TASK

    if text == _FILTER_OPTION_NONE:
        return FilterOption.NONE

    raise ValueError


def _get_task_uids_names(
    attributes_register: tasks.IAttributesRegisterView,
) -> Generator[tuple[tasks.UID, tasks.Name], None, None]:
    """Yield pairs of task UIDs and task names."""
    for uid, attributes in attributes_register.items():
        yield uid, attributes.name


def _format_task_uid_name_as_menu_option(
    task_uid: tasks.UID, task_name: tasks.Name
) -> str:
    return f"[{task_uid}] {task_name}" if task_name else f"[{task_uid}]"


def _get_menu_options(
    attributes_register: tasks.IAttributesRegisterView,
) -> Generator[str, None, None]:
    task_uids_names = sorted(
        _get_task_uids_names(attributes_register=attributes_register),
        key=lambda x: x[0],
    )
    for uid, name in task_uids_names:
        yield _format_task_uid_name_as_menu_option(uid, name)


def _parse_task_uid_from_menu_option(menu_option: str) -> tasks.UID:
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
            master=self._colouring_panel, text="Colouring"
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
                _FILTER_OPTION_SINGLE_TASK,
            ],
            state="readonly",
        )
        self._filter_options_dropdown.bind(
            "<<ComboboxSelected>>", lambda _: self._on_filter_option_selected()
        )
        self._filter_task_selection = tk.StringVar()
        self._filter_task_selection_dropdown = ttk.Combobox(
            self._filter_options_panel,
            textvariable=self._filter_task_selection,
            values=[
                "",
                *_get_menu_options(
                    self._logic_layer.get_task_system().attributes_register()
                ),
            ],
            state="disabled",
        )
        self._filter_task_selection_dropdown.bind(
            "<<ComboboxSelected>>", lambda _: self._update_figure()
        )
        self._update_task_to_filter_on_dropdown_options()
        self._show_completed_tasks = tk.BooleanVar()
        self._show_completed_tasks_checkbutton = ttk.Checkbutton(
            self._filter_panel,
            text="Show completed tasks",
            variable=self._show_completed_tasks,
            command=self._update_figure,
        )
        self._show_completed_tasks.set(False)

        self._static_graph = helpers.StaticTaskNetworkGraph(
            master=self,
            graph=tasks.NetworkGraph.empty(),
            get_task_annotation_text=self._get_formatted_task_name,
            get_task_properties=self._get_task_properties,
            get_hierarchy_properties=lambda _, __: RelationshipDrawingProperties(
                colour=DEFAULT_STANDARD_HIERARCHY_COLOUR,
                alpha=DEFAULT_STANDARD_RELATIONSHIP_ALPHA,
            ),
            get_dependency_properties=lambda _, __: RelationshipDrawingProperties(
                colour=DEFAULT_STANDARD_DEPENDENCY_COLOUR,
                alpha=DEFAULT_STANDARD_RELATIONSHIP_ALPHA,
            ),
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
        self._filter_task_selection_dropdown.grid(row=1, column=0)
        self._show_completed_tasks_checkbutton.grid(row=2, column=0)

        self._static_graph.grid(row=1, column=0)

        self._update_figure()

        broker = event_broker.get_singleton()
        broker.subscribe(event_broker.SystemModified, self._on_system_modified)
        broker.subscribe(event_broker.TaskSelected, self._on_task_selected)

    def _on_filter_option_selected(self) -> None:
        match _parse_filter_option(self._filter_selection.get()):
            case FilterOption.COMPONENT:
                self._filter_task_selection_dropdown["state"] = "readonly"
            case FilterOption.SINGLE_TASK:
                self._filter_task_selection_dropdown["state"] = "readonly"
            case FilterOption.NONE:
                self._filter_task_selection_dropdown["state"] = "disabled"
            case _:
                raise ValueError
        self._update_figure()

    def _get_task_to_filter_on(self) -> tasks.UID | None:
        text = self._filter_task_selection.get()
        if not text:
            return None

        return _parse_task_uid_from_menu_option(text)

    def _update_task_to_filter_on_dropdown_options(self) -> None:
        self._filter_task_selection_dropdown["values"] = [
            "",
            *_get_menu_options(
                self._logic_layer.get_task_system().attributes_register()
            ),
        ]

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

        self._update_task_to_filter_on_dropdown_options()

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
    ) -> RelationshipDrawingProperties:
        match _parse_colouring_option(self._colouring_selection.get()):
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
    ) -> RelationshipDrawingProperties:
        match _parse_colouring_option(self._colouring_selection.get()):
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

    def _get_task_properties(self, task: tasks.UID) -> TaskDrawingProperties:
        match _parse_colouring_option(self._colouring_selection.get()):
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

    def _get_standard_task_properties(self, task: tasks.UID) -> TaskDrawingProperties:
        if task == self._selected_task:
            colour = _STANDARD_SELECTED_TASK_COLOUR
            alpha = _STANDARD_SELECTED_TASK_ALPHA
        else:
            colour = _STANDARD_TASK_COLOUR
            alpha = _STANDARD_TASK_ALPHA

        return TaskDrawingProperties(
            colour=colour,
            alpha=alpha,
            label_colour=DEFAULT_TASK_LABEL_COLOUR,
        )

    def _get_standard_hierarchy_properties(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> RelationshipDrawingProperties:
        if self._selected_task in {supertask, subtask}:
            colour = _STANDARD_SELECTED_HIERARCHY_COLOUR
            alpha = _STANDARD_SELECTED_HIERARCHY_ALPHA
        else:
            colour = _STANDARD_HIERARCHY_COLOUR
            alpha = _STANDARD_HIERARCHY_ALPHA
        return RelationshipDrawingProperties(colour=colour, alpha=alpha)

    def _get_standard_dependency_properties(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> RelationshipDrawingProperties:
        if self._selected_task in {dependee_task, dependent_task}:
            colour = _STANDARD_SELECTED_DEPENDENCY_COLOUR
            alpha = _STANDARD_SELECTED_DEPENDENCY_ALPHA
        else:
            colour = _STANDARD_DEPENDENCY_COLOUR
            alpha = _STANDARD_DEPENDENCY_ALPHA
        return RelationshipDrawingProperties(colour=colour, alpha=alpha)

    def _get_importance_task_properties(self, task: tasks.UID) -> TaskDrawingProperties:
        match self._logic_layer.get_task_system().get_importance(task):
            case tasks.Importance.LOW:
                if task == self._selected_task:
                    colour = _IMPORTANCE_LOW_SELECTED_TASK_COLOUR
                    alpha = _IMPORTANCE_LOW_SELECTED_TASK_ALPHA
                else:
                    colour = _IMPORTANCE_LOW_TASK_COLOUR
                    alpha = _IMPORTANCE_LOW_TASK_ALPHA
            case tasks.Importance.MEDIUM:
                if task == self._selected_task:
                    colour = _IMPORTANCE_MEDIUM_SELECTED_TASK_COLOUR
                    alpha = _IMPORTANCE_MEDIUM_SELECTED_TASK_ALPHA
                else:
                    colour = _IMPORTANCE_MEDIUM_TASK_COLOUR
                    alpha = _IMPORTANCE_MEDIUM_TASK_ALPHA
            case tasks.Importance.HIGH:
                if task == self._selected_task:
                    colour = _IMPORTANCE_HIGH_SELECTED_TASK_COLOUR
                    alpha = _IMPORTANCE_HIGH_SELECTED_TASK_ALPHA
                else:
                    colour = _IMPORTANCE_HIGH_TASK_COLOUR
                    alpha = _IMPORTANCE_HIGH_TASK_ALPHA
            case None:
                if task == self._selected_task:
                    colour = _IMPORTANCE_NONE_SELECTED_TASK_COLOUR
                    alpha = _IMPORTANCE_NONE_SELECTED_TASK_ALPHA
                else:
                    colour = _IMPORTANCE_NONE_TASK_COLOUR
                    alpha = _IMPORTANCE_NONE_TASK_ALPA

        return TaskDrawingProperties(
            colour=colour,
            alpha=alpha,
            label_colour=DEFAULT_TASK_LABEL_COLOUR,
        )

    def _get_importance_hierarchy_properties(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> RelationshipDrawingProperties:
        if self._selected_task in {supertask, subtask}:
            colour = _IMPORTANCE_SELECTED_HIERARCHY_COLOUR
            alpha = _IMPORTANCE_SELECTED_HIERARCHY_ALPHA
        else:
            colour = _IMPORTANCE_HIERARCHY_COLOUR
            alpha = _IMPORTANCE_HIERARCHY_ALPHA
        return RelationshipDrawingProperties(colour=colour, alpha=alpha)

    def _get_importance_dependency_properties(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> RelationshipDrawingProperties:
        if self._selected_task in {dependee_task, dependent_task}:
            colour = _IMPORTANCE_SELECTED_DEPENDENCY_COLOUR
            alpha = _IMPORTANCE_SELECTED_DEPENDENCY_ALPHA
        else:
            colour = _IMPORTANCE_DEPENDENCY_COLOUR
            alpha = _IMPORTANCE_DEPENDENCY_ALPHA
        return RelationshipDrawingProperties(colour=colour, alpha=alpha)

    def _get_progress_task_properties(self, task: tasks.UID) -> TaskDrawingProperties:
        match self._logic_layer.get_task_system().get_progress(task):
            case tasks.Progress.NOT_STARTED:
                if task == self._selected_task:
                    colour = _PROGRESS_NOT_STARTED_SELECTED_TASK_COLOUR
                    alpha = _PROGRESS_NOT_STARTED_SELECTED_TASK_ALPHA
                else:
                    colour = _PROGRESS_NOT_STARTED_TASK_COLOUR
                    alpha = _PROGRESS_NOT_STARTED_TASK_ALPHA
            case tasks.Progress.IN_PROGRESS:
                if task == self._selected_task:
                    colour = _PROGRESS_IN_PROGRESS_SELECTED_TASK_COLOUR
                    alpha = _PROGRESS_IN_PROGRESS_SELECTED_TASK_ALPHA
                else:
                    colour = _PROGRESS_IN_PROGRESS_TASK_COLOUR
                    alpha = _PROGRESS_IN_PROGRESS_TASK_ALPHA
            case tasks.Progress.COMPLETED:
                if task == self._selected_task:
                    colour = _PROGRESS_COMPLETED_SELECTED_TASK_COLOUR
                    alpha = _PROGRESS_COMPLETED_SELECTED_TASK_ALPHA
                else:
                    colour = _PROGRESS_COMPLETED_TASK_COLOUR
                    alpha = _PROGRESS_COMPLETED_TASK_ALPHA
        return TaskDrawingProperties(
            colour=colour, alpha=alpha, label_colour=DEFAULT_TASK_LABEL_COLOUR
        )

    def _get_progress_hierarchy_properties(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> RelationshipDrawingProperties:
        if self._selected_task in {supertask, subtask}:
            colour = _PROGRESS_SELECTED_HIERARCHY_COLOUR
            alpha = _PROGRESS_SELECTED_HIERARCHY_ALPHA
        else:
            colour = _PROGRESS_HIERARCHY_COLOUR
            alpha = _PROGRESS_HIERARCHY_ALPHA
        return RelationshipDrawingProperties(colour=colour, alpha=alpha)

    def _get_progress_dependency_properties(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> RelationshipDrawingProperties:
        if self._selected_task in {dependee_task, dependent_task}:
            colour = _PROGRESS_SELECTED_DEPENDENCY_COLOUR
            alpha = _PROGRESS_SELECTED_DEPENDENCY_ALPHA
        else:
            colour = _PROGRESS_DEPENDENCY_COLOUR
            alpha = _PROGRESS_DEPENDENCY_ALPHA
        return RelationshipDrawingProperties(colour=colour, alpha=alpha)

    def _get_active_task_properties(self, task: tasks.UID) -> TaskDrawingProperties:
        if task == self._selected_task:
            if self._logic_layer.get_task_system().is_active_task(task):
                if (
                    self._logic_layer.get_task_system()
                    .network_graph()
                    .hierarchy_graph()
                    .is_concrete(task)
                ):
                    colour = _ACTIVE_ACTIVE_CONCRETE_SELECTED_TASK_COLOUR
                    alpha = _ACTIVE_ACTIVE_CONCRETE_SELECTED_TASK_ALPHA
                else:
                    colour = _ACTIVE_ACTIVE_NON_CONCRETE_SELECTED_TASK_COLOUR
                    alpha = _ACTIVE_ACTIVE_NON_CONCRETE_SELECTED_TASK_ALPHA
            elif (
                self._logic_layer.get_task_system().get_progress(task)
                is tasks.Progress.NOT_STARTED
            ):
                colour = _ACTIVE_INACTIVE_DOWNSTREAM_SELECTED_TASK_COLOUR
                alpha = _ACTIVE_INACTIVE_DOWNSTREAM_SELECTED_TASK_ALPHA
            else:
                colour = _ACTIVE_COMPLETED_SELECTED_TASK_COLOUR
                alpha = _ACTIVE_COMPLETED_SELECTED_TASK_ALPHA
        elif self._logic_layer.get_task_system().is_active_task(task):
            if (
                self._logic_layer.get_task_system()
                .network_graph()
                .hierarchy_graph()
                .is_concrete(task)
            ):
                colour = _ACTIVE_ACTIVE_CONCRETE_TASK_COLOUR
                alpha = _ACTIVE_ACTIVE_CONCRETE_TASK_ALPHA
            else:
                colour = _ACTIVE_ACTIVE_NON_CONCRETE_TASK_COLOUR
                alpha = _ACTIVE_ACTIVE_NON_CONCRETE_TASK_ALPHA
        elif (
            self._logic_layer.get_task_system().get_progress(task)
            is tasks.Progress.NOT_STARTED
        ):
            colour = _ACTIVE_INACTIVE_DOWNSTREAM_TASK_COLOUR
            alpha = _ACTIVE_INACTIVE_DOWNSTREAM_TASK_ALPHA
        else:
            colour = _ACTIVE_COMPLETED_TASK_COLOUR
            alpha = _ACTIVE_COMPLETED_TASK_ALPHA
        return TaskDrawingProperties(
            colour=colour, alpha=alpha, label_colour=DEFAULT_TASK_LABEL_COLOUR
        )

    def _get_active_hierarchy_properties(
        self, supertask: tasks.UID, subtask: tasks.UID
    ) -> RelationshipDrawingProperties:
        if self._selected_task in {supertask, subtask}:
            colour = _ACTIVE_SELECTED_HIERARCHY_COLOUR
            alpha = _ACTIVE_SELECTED_HIERARCHY_ALPHA
        else:
            colour = _ACTIVE_HIERARCHY_COLOUR
            alpha = _ACTIVE_HIERARCHY_ALPHA
        return RelationshipDrawingProperties(colour=colour, alpha=alpha)

    def _get_active_dependency_properties(
        self, dependee_task: tasks.UID, dependent_task: tasks.UID
    ) -> RelationshipDrawingProperties:
        if self._selected_task in {dependee_task, dependent_task}:
            colour = _ACTIVE_SELECTED_DEPENDENCY_COLOUR
            alpha = _ACTIVE_SELECTED_DEPENDENCY_ALPHA
        else:
            colour = _ACTIVE_DEPENDENCY_COLOUR
            alpha = _ACTIVE_DEPENDENCY_ALPHA
        return RelationshipDrawingProperties(colour=colour, alpha=alpha)

    def _get_filtered_graph(self) -> NetworkGraphView:
        if (filter_task := self._get_task_to_filter_on()) is not None:
            match _parse_filter_option(self._filter_selection.get()):
                case FilterOption.COMPONENT:
                    system = get_component_system(
                        filter_task, self._logic_layer.get_task_system()
                    )
                case FilterOption.SINGLE_TASK:
                    system = get_inferior_subsystem(
                        filter_task, self._logic_layer.get_task_system()
                    )
                case FilterOption.NONE:
                    system = self._logic_layer.get_task_system()
        else:
            system = self._logic_layer.get_task_system()

        # Need to check the system isn't empty of this will break
        if system and not self._show_completed_tasks.get():
            system = tasks.get_incomplete_system(system)

        return system.network_graph()

    def _update_figure(self) -> None:
        self._static_graph.update_graph(self._get_filtered_graph())
