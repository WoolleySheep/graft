from graft import graph
from graft.domain.task import task


class Dependencies:
    """Task dependencies.

    Acts as a DAG.
    """

    def __init__(
        self, directed_acyclic_graph: graph.DirectedAcyclicGraph[task.UID]
    ) -> None:
        """Initialise Hierarchies."""
        self._directed_acyclic_graph = directed_acyclic_graph

    def add_task(self, /, uid: task.UID) -> None:
        """Add a task."""
        try:
            self._directed_acyclic_graph.add_node(uid)
        except graph.NodeAlreadyExistsError as e:
            raise task.UIDAlreadyExistsError(uid) from e
        except Exception as e:
            raise e
