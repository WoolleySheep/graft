"""Task-specific classes and exceptions."""

from graft.domain.tasks.attributes import Attributes, AttributesView, IAttributesView
from graft.domain.tasks.attributes_register import (
    AttributesRegister,
    AttributesRegisterView,
    IAttributesRegisterView,
)
from graft.domain.tasks.dependency_graph import (
    DependencyAlreadyExistsError,
    DependencyDoesNotExistError,
    DependencyGraph,
    DependencyGraphView,
    DependencyIntroducesCycleError,
    DependencyLoopError,
    GraphDependenciesView,
    HasDependeeTasksError,
    HasDependentTasksError,
    IDependencyGraphView,
)
from graft.domain.tasks.description import Description
from graft.domain.tasks.helpers import TaskAlreadyExistsError, TaskDoesNotExistError
from graft.domain.tasks.hierarchy_graph import (
    HasSubTasksError,
    HasSuperTasksError,
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
    DependencyIntroducesHierarchyClashError,
    DependencyIntroducesNetworkCycleError,
    DependencyIntroducesStreamCycleError,
    DependencyPathAlreadyExistsFromSubTaskToSuperTaskError,
    DependencyPathAlreadyExistsFromSuperTaskToSubTaskError,
    HierarchyIntroducesDependencyClashError,
    HierarchyIntroducesNetworkCycleError,
    HierarchyPathAlreadyExistsFromDependeeTaskToDependentTaskError,
    HierarchyPathAlreadyExistsFromDependentTaskToDependeeTaskError,
    INetworkGraphView,
    NetworkGraph,
    NetworkGraphView,
    StreamPathFromDependentTaskToInferiorTaskOfDependeeTaskExistsError,
    StreamPathFromInferiorTaskOfDependentTaskToDependeeTaskExistsError,
    StreamPathFromInferiorTaskOfSubTaskToSuperTaskExistsError,
    StreamPathFromSubTaskToSuperTaskExistsError,
    StreamPathFromSuperTaskToInferiorTaskOfSubTaskExistsError,
    StreamPathFromSuperTaskToSubTaskExistsError,
)
from graft.domain.tasks.progress import Progress
from graft.domain.tasks.system import (
    DependeeIncompleteDependentStartedError,
    IncompleteDependeeTasksError,
    IncompleteDependeeTasksOfSuperiorTasksError,
    IncompleteDependeeTasksOfSuperiorTasksOfSupertaskError,
    IncompleteDependeeTasksOfSupertaskError,
    InferiorTaskHasImportanceError,
    ISystemView,
    MismatchedProgressForNewSupertaskError,
    MultipleImportancesInHierarchyError,
    NotConcreteTaskError,
    StartedDependentTasksError,
    StartedDependentTasksOfSuperiorTasksError,
    StartedDependentTasksOfSuperiorTasksOfSupertaskError,
    StartedDependentTasksOfSupertaskError,
    SubtaskHasImportanceError,
    SuperiorTaskHasImportanceError,
    SupertaskHasImportanceError,
    System,
    SystemView,
)
from graft.domain.tasks.uid import (
    UID,
    InvalidUIDNumberError,
    SubgraphTasksView,
    TasksView,
)
