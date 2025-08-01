import tkinter as tk
from collections.abc import Callable, Iterable

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.helpers.delete_dependency_error_windows import (
    convert_delete_dependency_exceptions_to_error_windows,
)
from graft.layers.presentation.tkinter_gui.tabs.dependency_panel.creation_deletion_panel.relationship_deletion_window import (
    RelationshipDeletionWindow,
)


class DependencyDeletionWindow(RelationshipDeletionWindow):
    def __init__(
        self,
        master: tk.Misc,
        dependency_options: Iterable[tuple[tasks.UID, tasks.UID]],
        delete_dependency: Callable[[tasks.UID, tasks.UID], None],
        get_task_name: Callable[[tasks.UID], tasks.Name],
    ) -> None:
        super().__init__(
            master=master,
            title="Delete Dependency",
            relationship_options=dependency_options,
            get_task_name=get_task_name,
            delete_relationship=lambda dependee_task,
            dependent_task: convert_delete_dependency_exceptions_to_error_windows(
                func=lambda: delete_dependency(dependee_task, dependent_task),
                get_task_name=get_task_name,
                master=master,
            ),
        )
