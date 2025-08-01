"""Task-specific classes and exceptions."""

from graft.domain.tasks.attributes import Attributes, AttributesView, IAttributesView
from graft.domain.tasks.attributes_register import (
    AttributesRegister,
    AttributesRegisterView,
    IAttributesRegisterView,
)
from graft.domain.tasks.dependency_graph import (
    DependenciesView,
    DependencyAlreadyExistsError,
    DependencyDoesNotExistError,
    DependencyGraph,
    DependencyGraphView,
    DependencyIntroducesCycleError,
    DependencyLoopError,
    IDependencyGraphView,
)
from graft.domain.tasks.description import Description
from graft.domain.tasks.graph_processing import (
    get_component_system,
    get_incomplete_system,
    get_inferior_subgraph,
    get_superior_subgraph,
)
from graft.domain.tasks.helpers import (
    TaskAlreadyExistsError,
    TaskDoesNotExistError,
)
from graft.domain.tasks.hierarchy_graph import (
    HierarchiesView,
    HierarchyAlreadyExistsError,
    HierarchyDoesNotExistError,
    HierarchyGraph,
    HierarchyGraphView,
    HierarchyIntroducesCycleError,
    HierarchyIntroducesRedundantHierarchyError,
    HierarchyLoopError,
    IHierarchyGraphView,
)
from graft.domain.tasks.importance import Importance
from graft.domain.tasks.name import Name
from graft.domain.tasks.network_graph import (
    DependencyBetweenHierarchyLevelsError,
    DependencyIntroducesDependencyCrossoverError,
    DependencyIntroducesDependencyDuplicationError,
    DependencyIntroducesNetworkCycleError,
    HasNeighboursError,
    HierarchyIntroducesDependencyCrossoverError,
    HierarchyIntroducesDependencyDuplicationError,
    HierarchyIntroducesNetworkCycleError,
    INetworkGraphView,
    NetworkGraph,
    NetworkGraphView,
)
from graft.domain.tasks.progress import Progress
from graft.domain.tasks.system import (
    DependeeIncompleteDependentStartedError,
    DownstreamTasksHaveStartedError,
    DownstreamTasksOfSupertaskHaveStartedError,
    InferiorTasksHaveImportanceError,
    ISystemView,
    MismatchedProgressForNewSupertaskError,
    MultipleImportancesInHierarchyError,
    NotConcreteTaskError,
    SuperiorTasksHaveImportanceError,
    System,
    SystemView,
    UpstreamTasksAreIncompleteError,
    UpstreamTasksOfSupertaskAreIncompleteError,
)
from graft.domain.tasks.uid import (
    UID,
    InvalidUIDNumberError,
    TasksView,
)
