"""Standard logic-layer implementation and associated exceptions."""

from typing import override

from graft import architecture
from graft.domain import tasks


class StandardLogicLayer(architecture.LogicLayer):
    """Standard logic layer."""

    def __init__(self, data_layer: architecture.DataLayer) -> None:
        """Initialise StandardLogicLayer."""
        super().__init__(data_layer=data_layer)

    @override
    def initialise(self) -> None:
        """Initialise the standard logic layer, as well as the underlying data-layer."""
        self._data_layer.initialise()

    @override
    def create_task(self) -> tasks.UID:
        uid = self._data_layer.get_next_task_uid()
        system = self._data_layer.load_system()
        system.add_task(uid)
        self._data_layer.save_system(system=system)
        self._data_layer.increment_next_task_uid_counter()
        return uid
