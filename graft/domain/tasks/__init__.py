"""Task-specific classes and exceptions."""

from graft.domain.tasks.attributes import Attributes, AttributesView
from graft.domain.tasks.attributes_register import (
    AttributesRegister,
    AttributesRegisterView,
)
from graft.domain.tasks.dependency_graph import (
    DependenciesView,
    DependencyAlreadyExistsError,
    DependencyDoesNotExistError,
    DependencyGraph,
    DependencyGraphView,
    DependencyIntroducesCycleError,
    DependencyLoopError,
    HasDependeeTasksError,
    HasDependentTasksError,
    IDependencyGraphView,
    InverseDependencyAlreadyExistsError,
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
    HierarchyLoopError,
    HierarchyPathAlreadyExistsError,
    IHierarchyGraphView,
    InverseHierarchyAlreadyExistsError,
    SubTaskIsAlreadySubTaskOfSuperiorTaskOfSuperTaskError,
)
from graft.domain.tasks.importance import Importance
from graft.domain.tasks.name import Name
from graft.domain.tasks.progress import Progress
from graft.domain.tasks.system import (
    DependeeIncompleteDependentStartedError,
    DependencyIntroducesHierarchyClashError,
    DependencyIntroducesStreamCycleError,
    DependencyPathAlreadyExistsFromSubTaskToSuperTaskError,
    DependencyPathAlreadyExistsFromSuperTaskToSubTaskError,
    HierarchyIntroducesDependencyClashError,
    HierarchyPathAlreadyExistsFromDependeeTaskToDependentTaskError,
    HierarchyPathAlreadyExistsFromDependentTaskToDependeeTaskError,
    IncompleteDependeeTasksError,
    IncompleteDependeeTasksOfSuperiorTasksError,
    IncompleteDependeeTasksOfSuperiorTasksOfSupertaskError,
    IncompleteDependeeTasksOfSupertaskError,
    MismatchedProgressForNewSupertaskError,
    NotConcreteTaskError,
    StartedDependentTasksError,
    StartedDependentTasksOfSuperiorTasksError,
    StartedDependentTasksOfSuperiorTasksOfSupertaskError,
    StartedDependentTasksOfSupertaskError,
    StreamPathFromDependentTaskToInferiorTaskOfDependeeTaskExistsError,
    StreamPathFromInferiorTaskOfDependentTaskToDependeeTaskExistsError,
    StreamPathFromInferiorTaskOfSubTaskToSuperTaskExistsError,
    StreamPathFromSubTaskToSuperTaskExistsError,
    StreamPathFromSuperTaskToInferiorTaskOfSubTaskExistsError,
    StreamPathFromSuperTaskToSubTaskExistsError,
    System,
    SystemView,
)
from graft.domain.tasks.uid import (
    UID,
    InvalidUIDNumberError,
    UIDsView,
)
