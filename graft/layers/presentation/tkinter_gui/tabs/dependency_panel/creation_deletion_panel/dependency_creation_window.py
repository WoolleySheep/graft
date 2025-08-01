import tkinter as tk
from collections.abc import Callable, Iterable

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.helpers.create_dependency_error_windows import (
    convert_create_dependency_exceptions_to_error_windows,
)
from graft.layers.presentation.tkinter_gui.tabs.dependency_panel.creation_deletion_panel.relationship_creation_window import (
    RelationshipCreationWindow,
)


class DependencyCreationWindow(RelationshipCreationWindow):
    def __init__(
        self,
        master: tk.Misc,
        get_tasks: Callable[[], Iterable[tasks.UID]],
        get_incomplete_tasks: Callable[[], Iterable[tasks.UID]],
        get_task_name: Callable[[tasks.UID], tasks.Name],
        create_dependency: Callable[[tasks.UID, tasks.UID], None],
        fixed_dependee_task: tasks.UID | None = None,
        fixed_dependent_task: tasks.UID | None = None,
    ) -> None:
        super().__init__(
            master=master,
            title="Create Dependency",
            source_label_text="Dependee-task: ",
            target_label_text="Dependent-task: ",
            get_tasks=get_tasks,
            get_incomplete_tasks=get_incomplete_tasks,
            get_task_name=get_task_name,
            create_relationship=lambda dependee_task,
            dependent_task: convert_create_dependency_exceptions_to_error_windows(
                func=lambda: create_dependency(dependee_task, dependent_task),
                get_task_name=get_task_name,
                master=self,
            ),
            fixed_source=fixed_dependee_task,
            fixed_target=fixed_dependent_task,
        )
