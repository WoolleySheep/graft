import tkinter as tk
from collections.abc import Callable, Iterable

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.helpers.create_hierarchy_error_windows import (
    convert_create_hierarchy_exceptions_to_error_windows,
)
from graft.layers.presentation.tkinter_gui.tabs.dependency_panel.creation_deletion_panel.relationship_creation_window import (
    RelationshipCreationWindow,
)


class HierarchyCreationWindow(RelationshipCreationWindow):
    def __init__(
        self,
        master: tk.Misc,
        get_tasks: Callable[[], Iterable[tasks.UID]],
        get_incomplete_tasks: Callable[[], Iterable[tasks.UID]],
        get_task_name: Callable[[tasks.UID], tasks.Name],
        create_hierarchy: Callable[[tasks.UID, tasks.UID], None],
        fixed_supertask: tasks.UID | None = None,
        fixed_subtask: tasks.UID | None = None,
    ) -> None:
        super().__init__(
            master=master,
            title="Create Hierarchy",
            source_label_text="Super-task: ",
            target_label_text="Sub-task: ",
            get_tasks=get_tasks,
            get_incomplete_tasks=get_incomplete_tasks,
            get_task_name=get_task_name,
            create_relationship=lambda supertask,
            subtask: convert_create_hierarchy_exceptions_to_error_windows(
                func=lambda: create_hierarchy(supertask, subtask),
                get_task_name=get_task_name,
                master=self,
            ),
            fixed_source=fixed_supertask,
            fixed_target=fixed_subtask,
        )
