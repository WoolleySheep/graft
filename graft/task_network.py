import collections
import datetime
from typing import (
    Callable,
    Collection,
    Generator,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
)

import networkx as nx
from attr import attr

from graft.acyclic_digraph import (
    AcyclicDiGraph,
    EdgeDoesNotExistError,
    NodeDoesNotExistError,
    NotReachableError,
    SelfLoopError,
)
from graft.constrained_graph import (
    ConstrainedGraph,
    NoTargetPredecessorsAsSourceAncestorsError,
)
from graft.priority import Priority
from graft.task_attributes import (
    AfterDueDatetimeError,
    BeforeStartDatetimeError,
    TaskAttributes,
)


class TaskDoesNotExistError(Exception):
    def __init__(self, uid: str, *args, **kwargs):
        self.uid = uid

        super().__init__(f"task [{uid}] does not exist", *args, **kwargs)


class HierarchyExistsError(Exception):
    def __init__(self, uid1: str, uid2: str, *args, **kwargs):
        self.uid1 = uid1
        self.uid2 = uid2

        super().__init__(
            f"hierarchy from [{uid1}] -> [{uid2}] already exists", *args, **kwargs
        )


class InverseHierarchyExistsError(Exception):
    def __init__(self, uid1: str, uid2: str, *args, **kwargs):
        self.uid1 = uid2
        self.uid2 = uid1

        super().__init__(
            f"hierarchy from [{uid1}] -> [{uid2}] already exists", *args, **kwargs
        )


class SelfHierarchyError(Exception):
    def __init__(self, uid: str, *args, **kwargs):
        self.uid = uid

        super().__init__(
            "hierarchy cannot be added from a task to itself", *args, **kwargs
        )


class InferiorTaskError(Exception):
    def __init__(self, uid1: str, uid2: str, digraph: nx.DiGraph, *args, **kwargs):
        self.uid1 = uid1
        self.uid2 = uid2
        self.digraph = digraph

        # TODO: Add Error message
        super().__init__("", *args, **kwargs)


class SuperiorTasksError(Exception):
    def __init__(self, uid1: str, uid2: str, superior_tasks: set[str], *args, **kwargs):
        self.uid1 = uid1
        self.uid2 = uid2
        self.superior_tasks = superior_tasks

        # TODO: Add Error message
        super().__init__("", *args, **kwargs)


class HierarchyIntroducesCycleError(Exception):
    def __init__(self, uid1: str, uid2: str, digraph: nx.DiGraph, *args, **kwargs):
        self.uid1 = uid1
        self.uid2 = uid2
        self.digraph = digraph

        # TODO: Add Error message
        super().__init__("", *args, **kwargs)


class HierarchyDoesNotExistError(Exception):
    def __init__(self, uid1: str, uid2: str, *args, **kwargs):
        self.uid1 = uid1
        self.uid2 = uid2

        super().__init__(
            f"hierarchy from [{uid1}] -> [{uid2}] does not exist", *args, **kwargs
        )


class DependencyExistsError(Exception):
    def __init__(self, uid1: str, uid2: str, *args, **kwargs):
        self.uid1 = uid1
        self.uid2 = uid2

        super().__init__(
            f"dependency from [{uid1}] -> [{uid2}] already exists", *args, **kwargs
        )


class InverseDependencyExistsError(Exception):
    def __init__(self, uid1: str, uid2: str, *args, **kwargs):
        self.uid1 = uid2
        self.uid2 = uid1

        super().__init__(
            f"dependency from [{uid1}] -> [{uid2}] already exists", *args, **kwargs
        )


class SelfDependencyError(Exception):
    def __init__(self, uid: str, *args, **kwargs):
        self.uid = uid

        super().__init__(
            "dependency cannot be added from a task to itself", *args, **kwargs
        )


class DependencyIntroducesCycleError(Exception):
    def __init__(self, uid1: str, uid2: str, digraph: nx.DiGraph, *args, **kwargs):
        self.uid1 = uid1
        self.uid2 = uid2
        self.digraph = digraph

        # TODO: Add Error message
        super().__init__("", *args, **kwargs)


class DependencyDoesNotExistError(Exception):
    def __init__(self, uid1: str, uid2: str, *args, **kwargs):
        self.uid1 = uid1
        self.uid2 = uid2

        super().__init__(
            f"dependency from [{uid1}] -> [{uid2}] does not exist", *args, **kwargs
        )


class HasSuperTasksError(Exception):
    def __init__(self, uid: str, supertasks: Collection[str], *args, **kwargs):
        self.uid = uid
        self.supertasks = supertasks

        # TODO: Add error message
        super().__init__("", *args, **kwargs)


class HasSubTasksError(Exception):
    def __init__(self, uid: str, subtasks: Collection[str], *args, **kwargs):
        self.uid = uid
        self.subtasks = subtasks

        # TODO: Add error message
        super().__init__("", *args, **kwargs)


class HasDependentTasksError(Exception):
    def __init__(self, uid: str, dependent_tasks: Collection[str], *args, **kwargs):
        self.uid = uid
        self.dependent_tasks = dependent_tasks

        # TODO: Add error message
        super().__init__("", *args, **kwargs)


class HasDependeeTasksError(Exception):
    def __init__(self, uid: str, dependee_tasks: Collection[str], *args, **kwargs):
        self.uid = uid
        self.dependee_tasks = dependee_tasks

        # TODO: Add error message
        super().__init__("", *args, **kwargs)


class TaskCycleError(Exception):
    def __init__(self, uid1: str, uid2: str, *args, **kwargs):
        self.uid1 = uid1
        self.uid2 = uid2

        # TODO: Add error message
        super().__init__("", *args, **kwargs)


class TaskCycle1UpstreamOf2Error(TaskCycleError):
    ...


class TaskCycle1DownstreamOf2Error(TaskCycleError):
    ...


class TaskCycleInferiorOf2UpstreamOf1(TaskCycleError):
    ...


class TaskCycleInferiorOf2DownstreamOf1(TaskCycleError):
    ...


class TaskCycleDependencyInferiorOf1DownstreamOf2(TaskCycleError):
    ...


class TaskCycleDependencySuperiorOf1DownstreamOf2(TaskCycleError):
    ...


class TaskCycleDependencyInferiorOf2UpstreamOf1(TaskCycleError):
    ...


class TaskCycleDependencySuperiorOf2UpstreamOf1(TaskCycleError):
    ...


class DependencyHierarchyClashError(Exception):
    def __init__(
        self, supertask: str, subtask: str, uid1: str, uid2: str, *args, **kwargs
    ):
        self.supertask = supertask
        self.subtask = subtask
        self.uid1 = uid1
        self.uid2 = uid2

        # TODO: Add error message
        super().__init__("", *args, **kwargs)


class DependencyHierarchyExtendedClashError(Exception):
    def __init__(self, uid1: str, uid2: str, *args, **kwargs):
        self.uid1 = uid1
        self.uid2 = uid2

        # TODO: Add error message
        super().__init__("", *args, **kwargs)


class DependencyDownstreamCycleError(Exception):
    def __init__(self, uid1: str, uid2: str, *args, **kwargs):
        self.uid1 = uid1
        self.uid2 = uid2

        # TODO: Add error message
        super().__init__("", *args, **kwargs)


class DependencyCycleInferiorOf2UpstreamOf1(Exception):
    def __init__(self, uid1: str, uid2: str, *args, **kwargs):
        self.uid1 = uid1
        self.uid2 = uid2

        # TODO: Add error message
        super().__init__("", *args, **kwargs)


class DependencyCycleInferiorOf1DownstreamOf2(Exception):
    def __init__(self, uid1: str, uid2: str, *args, **kwargs):
        self.uid1 = uid1
        self.uid2 = uid2

        # TODO: Add error message
        super().__init__("", *args, **kwargs)


class MultiplePrioritiesInHierarchyError(Exception):
    def __init__(self, uid1: str, uid2: str, *args, **kwargs):
        self.uid1 = uid1
        self.uid2 = uid2

        # TODO: Add error message
        super().__init__("", *args, **kwargs)


class SuperiorTaskPrioritiesError(Exception):
    def __init__(
        self,
        uid: str,
        task_attributes_map: Mapping[str, TaskAttributes],
        task_hierarchy: ConstrainedGraph,
        *args,
        **kwargs,
    ):
        self.uid = uid
        self.superior_tasks_with_priorities = []

        # TODO: Decide on whether to calculate subgraph instead
        unsearched_tasks = collections.deque(task_hierarchy.predecessors(node=uid))
        searched_tasks = set()
        while unsearched_tasks:
            task = unsearched_tasks.popleft()
            searched_tasks.add(task)
            priority = task_attributes_map[task].priority
            if priority:
                self.superior_tasks_with_priorities.append(task)
                continue

            for supertask in task_hierarchy.predecessors(node=task):
                if supertask not in searched_tasks:
                    unsearched_tasks.append(supertask)

        formatted_superior_tasks_and_priorities = [
            f"[{uid}]: [{task_attributes_map[uid].priority}]"
            for uid in self.superior_tasks_with_priorities
        ]
        superior_tasks_and_priorities_formatted = ", ".join(
            formatted_superior_tasks_and_priorities
        )

        super().__init__(
            f"task [{uid}] has superior tasks with priorities: {superior_tasks_and_priorities_formatted}",
            *args,
            **kwargs,
        )


class TaskNetwork:
    def __init__(
        self,
        task_attributes_map: Mapping[str, TaskAttributes],
        task_hierarchy: ConstrainedGraph,
        task_dependencies: AcyclicDiGraph,
    ) -> None:
        self._task_attributes_map = task_attributes_map
        self._task_hierarchy = task_hierarchy
        self._task_dependencies = task_dependencies

    def add_task(self, uid: str) -> None:
        """Add a task to the network.

        Assumed that no tasks will be added with existing uid's.
        """
        self._task_attributes_map[uid] = TaskAttributes()
        self._task_hierarchy.add_node(node=uid)
        self._task_dependencies.add_node(node=uid)

    def remove_task(self, uid: str) -> None:
        """Remove a task from the network."""
        if uid not in self._task_attributes_map:
            raise TaskDoesNotExistError(uid=uid)

        if supertasks := set(self._task_hierarchy.predecessors(node=uid)):
            raise HasSuperTasksError(uid=uid, supertasks=supertasks)

        if subtasks := set(self._task_hierarchy.successors(node=uid)):
            raise HasSubTasksError(uid=uid, subtasks=subtasks)

        if dependee_tasks := set(self._task_dependencies.predecessors(node=uid)):
            raise HasDependeeTasksError(uid=uid, dependee_tasks=dependee_tasks)

        if dependent_tasks := set(self._task_dependencies.successors(node=uid)):
            raise HasDependentTasksError(uid=uid, dependent_tasks=dependent_tasks)

        del self._task_attributes_map[uid]
        self._task_hierarchy.remove_node(node=uid)
        self._task_dependencies.remove_node(node=uid)

    def add_hierarchy(self, uid1: str, uid2: str) -> None:
        for uid in (uid1, uid2):
            if uid not in self._task_attributes_map:
                raise TaskDoesNotExistError(uid=uid)

        if uid1 == uid2:
            raise SelfHierarchyError(uid=uid1)

        if self._task_hierarchy.has_edge(source=uid1, target=uid2):
            raise HierarchyExistsError(uid1=uid1, uid2=uid2)

        if self._task_hierarchy.has_edge(source=uid2, target=uid1):
            raise InverseHierarchyExistsError(uid1=uid1, uid2=uid2)

        try:
            inferior_check_digraph = self._task_hierarchy.get_joining_subgraph(
                source=uid1, target=uid2
            )
        except NotReachableError:
            pass
        else:
            raise InferiorTaskError(
                uid1=uid1, uid2=uid2, digraph=inferior_check_digraph
            )

        try:
            superior_tasks = (
                self._task_hierarchy.get_target_predecessors_that_are_source_ancestors(
                    source=uid1, target=uid2
                )
            )
        except NoTargetPredecessorsAsSourceAncestorsError:
            pass
        else:
            raise SuperiorTasksError(
                uid1=uid1, uid2=uid2, superior_tasks=superior_tasks
            )

        try:
            cycle_digraph = self._task_hierarchy.get_joining_subgraph(
                source=uid2, target=uid1
            )
        except NotReachableError:
            pass
        else:
            raise HierarchyIntroducesCycleError(
                uid1=uid1, uid2=uid2, digraph=cycle_digraph
            )

        is_uid1_upstream_of_uid2 = self.is_downstream(uid1=uid1, uid2=uid2)
        if is_uid1_upstream_of_uid2:
            raise TaskCycle1UpstreamOf2Error(uid1=uid1, uid2=uid2)

        is_uid1_downstream_of_uid2 = self.is_downstream(uid1=uid2, uid2=uid1)
        if is_uid1_downstream_of_uid2:
            raise TaskCycle1DownstreamOf2Error(uid1=uid1, uid2=uid2)

        is_inferior_of_uid2_downstream_of_uid1 = self._is_inferior_downstream(
            uid1=uid2, uid2=uid1
        )
        if is_inferior_of_uid2_downstream_of_uid1:
            raise TaskCycleInferiorOf2DownstreamOf1(uid1=uid1, uid2=uid2)

        is_inferior_of_uid2_upstream_of_uid1 = self._is_inferior_upstream(
            uid1=uid2, uid2=uid1
        )
        if is_inferior_of_uid2_upstream_of_uid1:
            raise TaskCycleInferiorOf2UpstreamOf1(uid1=uid1, uid2=uid2)

        # TODO: Consider raising exception if adding a hierarchy means that two
        # tasks, one superior to the other, are both independently upstream of a
        # third task. The superior task being upstream means that all inferior
        # tasks are also upstream, duplicating information. Find a way to block
        # this.

        supertask_has_priority = bool(self._task_attributes_map[uid1].priority)
        subtask_has_priority = bool(self._task_attributes_map[uid2].priority)

        if (
            supertask_has_priority
            or self._do_any_superior_tasks_have_priority(uid=uid1)
        ) and (subtask_has_priority or self._do_any_inferior_tasks_have_priority(uid2)):
            raise MultiplePrioritiesInHierarchyError(uid1=uid1, uid2=uid2)

        self._do_any_inferior_tasks_have_priority(uid2)

        # TODO: Replace with simplified version, as checks already done here
        self._task_hierarchy.add_edge(source=uid1, target=uid2)

    def remove_hierarchy(self, uid1: str, uid2: str) -> None:
        try:
            self._task_hierarchy.remove_edge(source=uid1, target=uid2)
        except NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(uid=e.node) from e
        except SelfLoopError as e:
            raise SelfHierarchyError(uid=uid1) from e
        except EdgeDoesNotExistError as e:
            raise HierarchyDoesNotExistError(uid1=uid1, uid2=uid2) from e

    def add_dependency(self, uid1: str, uid2: str) -> None:
        for uid in (uid1, uid2):
            if uid not in self._task_attributes_map:
                raise TaskDoesNotExistError(uid=uid)

        if uid1 == uid2:
            raise SelfDependencyError(uid=uid1)

        if self._task_dependencies.has_edge(source=uid1, target=uid2):
            raise DependencyExistsError(uid1=uid1, uid2=uid2)

        if self._task_dependencies.has_edge(source=uid2, target=uid1):
            raise InverseDependencyExistsError(uid1=uid1, uid2=uid2)

        try:
            cycle_digraph = self._task_dependencies.get_joining_subgraph(
                source=uid2, target=uid1
            )
        except NotReachableError:
            pass
        else:
            raise DependencyIntroducesCycleError(
                uid1=uid1, uid2=uid2, digraph=cycle_digraph
            )

        if self._task_hierarchy.has_edge(source=uid1, target=uid2):
            raise DependencyHierarchyClashError(
                supertask=uid1, subtask=uid2, uid1=uid1, uid2=uid2
            )

        if self._task_hierarchy.has_edge(source=uid2, target=uid1):
            raise DependencyHierarchyClashError(
                supertask=uid2, subtask=uid1, uid1=uid1, uid2=uid2
            )

        if self._task_hierarchy.has_joining_subgraph(source=uid1, target=uid2):
            raise DependencyHierarchyExtendedClashError(uid1=uid1, uid2=uid2)

        if self._task_hierarchy.has_joining_subgraph(source=uid2, target=uid1):
            raise DependencyHierarchyExtendedClashError(uid1=uid1, uid2=uid2)

        if self.is_downstream(uid1=uid2, uid2=uid1):
            raise DependencyDownstreamCycleError(uid1=uid1, uid2=uid2)

        if self._is_inferior_upstream(uid1=uid2, uid2=uid1):
            raise DependencyCycleInferiorOf2UpstreamOf1(uid1=uid1, uid2=uid2)

        if self._is_inferior_downstream(uid1=uid1, uid2=uid2):
            raise DependencyCycleInferiorOf1DownstreamOf2(uid1=uid1, uid2=uid2)

        # TODO: Replace with simplified version, as checks already done here
        self._task_dependencies.add_edge(source=uid1, target=uid2)

    def remove_dependency(self, uid1: str, uid2: str) -> None:
        try:
            self._task_dependencies.remove_edge(source=uid1, target=uid2)
        except NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(uid=e.node) from e
        except SelfLoopError as e:
            raise SelfDependencyError(uid=uid1) from e
        except EdgeDoesNotExistError as e:
            raise DependencyDoesNotExistError(uid1=uid1, uid2=uid2) from e

    def _get_superior_of_1_or_1_upstream_of_2(self, uid1: str, uid2: str) -> set[str]:
        superior_tasks = self._task_hierarchy.ancestors(node=uid1)
        superior_tasks.add(uid1)

        superior_of_1_or_1_upstream_of_2 = set()

        for upstream_task in self.upstream_tasks(
            uid=uid2, stop_search_condition=lambda uid: uid in superior_tasks
        ):
            if upstream_task in superior_tasks:
                superior_of_1_or_1_upstream_of_2.add(upstream_task)

        return superior_of_1_or_1_upstream_of_2

    def _get_superior_of_1_or_1_downstream_of_2(self, uid1: str, uid2: str) -> set[str]:
        superior_tasks = self._task_hierarchy.ancestors(node=uid1)
        superior_tasks.add(uid1)

        superior_of_1_or_1_downstream_of_2 = set()

        for task in self.downstream_tasks(
            uid=uid2, stop_search_condition=lambda uid: uid in superior_tasks
        ):
            if task in superior_tasks:
                superior_of_1_or_1_downstream_of_2.add(task)

        return superior_of_1_or_1_downstream_of_2

    def upstream_tasks(
        self, uid: str, stop_search_condition: Optional[Callable[[str], bool]] = None
    ) -> Iterator[str]:
        """Get all upstream tasks of a given task with no duplicates.

        In this context, upstream means any tasks which must be completed for a
        given task to begin.

        If the iterator encounters a task that fulfils the
        stop_search_condition, it will still yield the task, but it will not
        keep searching upstream of that task. This doesn't mean that those tasks
        won't be yielded, as they may be accessible upstream of another task.
        """
        # TODO: Rework - look at all the code duplication
        tasks_to_assess = set(self._task_dependencies.predecessors(node=uid))
        supertasks_to_assess = set(self._task_hierarchy.predecessors(node=uid))
        supertasks_assessed = set()
        yielded_tasks = set()

        while tasks_to_assess or supertasks_to_assess:
            while tasks_to_assess:
                task = tasks_to_assess.pop()
                yield task
                yielded_tasks.add(task)

                if stop_search_condition is not None and stop_search_condition(task):
                    continue

                supertasks = set(self._task_hierarchy.predecessors(node=task))
                supertasks.difference_update(supertasks_to_assess)
                supertasks.difference_update(supertasks_assessed)
                supertasks.difference_update(tasks_to_assess)
                supertasks.difference_update(yielded_tasks)
                supertasks_to_assess.update(supertasks)

                subtasks = set(self._task_hierarchy.successors(node=task))
                subtasks.difference_update(tasks_to_assess)
                subtasks.difference_update(yielded_tasks)
                tasks_to_assess.update(subtasks)

                dependee_tasks = set(self._task_dependencies.predecessors(node=task))
                dependee_tasks.difference_update(tasks_to_assess)
                dependee_tasks.difference_update(yielded_tasks)
                tasks_to_assess.update(dependee_tasks)

                supertasks_assessed.add(task)

            if supertasks_to_assess:
                task = supertasks_to_assess.pop()

                supertasks = set(self._task_hierarchy.predecessors(node=task))
                supertasks.difference_update(supertasks_to_assess)
                supertasks.difference_update(supertasks_assessed)
                supertasks.difference_update(tasks_to_assess)
                supertasks.difference_update(yielded_tasks)
                supertasks_to_assess.update(supertasks)

                dependee_tasks = set(self._task_dependencies.predecessors(node=task))
                dependee_tasks.difference_update(tasks_to_assess)
                dependee_tasks.difference_update(yielded_tasks)
                tasks_to_assess.update(dependee_tasks)

                supertasks_assessed.add(task)

    def downstream_tasks(
        self, uid: str, stop_search_condition: Optional[Callable[[str], bool]] = None
    ) -> Iterator[str]:
        """Get all downstream tasks of a given task with no duplicates.

        In this context, downstream means any task which relies on the given
        task being completed to begin.

        If the iterator encounters a task that fulfils the
        stop_search_condition, it will still yield the task, but it will not
        keep searching downstream of that task. This doesn't mean that those tasks
        won't be yielded, as they may be accessible downstream of another task.
        """
        tasks_to_assess = set(self._task_dependencies.successors(node=uid))
        supertasks_to_assess = set(self._task_hierarchy.predecessors(node=uid))
        supertasks_assessed = set()
        yielded_tasks = set()

        while tasks_to_assess or supertasks_to_assess:
            while tasks_to_assess:
                task = tasks_to_assess.pop()
                yield task
                yielded_tasks.add(task)

                if stop_search_condition is not None and stop_search_condition(task):
                    continue

                supertasks = set(self._task_hierarchy.predecessors(node=task))
                supertasks.difference_update(supertasks_assessed)
                supertasks.difference_update(tasks_to_assess)
                supertasks.difference_update(yielded_tasks)
                supertasks_to_assess.update(supertasks)

                subtasks = set(self._task_hierarchy.successors(node=task))
                subtasks.difference_update(yielded_tasks)
                tasks_to_assess.update(subtasks)

                dependee_tasks = set(self._task_dependencies.successors(node=task))
                dependee_tasks.difference_update(yielded_tasks)
                tasks_to_assess.update(dependee_tasks)

                supertasks_assessed.add(task)

            if supertasks_to_assess:
                task = supertasks_to_assess.pop()

                supertasks = set(self._task_hierarchy.predecessors(node=task))
                supertasks.difference_update(supertasks_assessed)
                supertasks.difference_update(tasks_to_assess)
                supertasks.difference_update(yielded_tasks)
                supertasks_to_assess.update(supertasks)

                dependee_tasks = set(self._task_dependencies.successors(node=task))
                dependee_tasks.difference_update(yielded_tasks)
                tasks_to_assess.update(dependee_tasks)

                supertasks_assessed.add(task)

    def is_downstream(self, uid1: str, uid2: str) -> bool:
        """Is uid2 downstream of uid1.

        In this context, downstream means any task which relies on the given
        task being completed to begin."""

        tasks_to_assess = set(self._task_dependencies.successors(node=uid1))
        tasks_assessed = set()
        supertasks_to_assess = set(self._task_hierarchy.predecessors(node=uid1))
        supertasks_assessed = set()

        while tasks_to_assess or supertasks_to_assess:
            while tasks_to_assess:
                task = tasks_to_assess.pop()
                if task == uid2:
                    return True

                supertasks = set(self._task_hierarchy.predecessors(node=task))
                supertasks.difference_update(supertasks_assessed)
                supertasks.difference_update(tasks_to_assess)
                supertasks.difference_update(tasks_assessed)
                supertasks_to_assess.update(supertasks)

                subtasks = set(self._task_hierarchy.successors(node=task))
                subtasks.difference_update(tasks_assessed)
                tasks_to_assess.update(subtasks)

                dependee_tasks = set(self._task_dependencies.successors(node=task))
                dependee_tasks.difference_update(tasks_assessed)
                tasks_to_assess.update(dependee_tasks)

                tasks_assessed.add(task)
                supertasks_assessed.add(task)

            if supertasks_to_assess:
                task = supertasks_to_assess.pop()

                supertasks = set(self._task_hierarchy.predecessors(node=task))
                supertasks.difference_update(supertasks_assessed)
                supertasks.difference_update(tasks_to_assess)
                supertasks.difference_update(tasks_assessed)
                supertasks_to_assess.update(supertasks)

                dependee_tasks = set(self._task_dependencies.successors(node=task))
                dependee_tasks.difference_update(tasks_assessed)
                tasks_to_assess.update(dependee_tasks)

                supertasks_assessed.add(task)

        return False

    def _is_inferior_downstream(self, uid1: str, uid2: str) -> bool:
        """Is a task inferior to uid1 downstream of uid2."""
        inferior_to_uid1 = set(self._task_hierarchy.descendants(node=uid1))
        downstream_of_uid2 = set(self.downstream_tasks(uid=uid2))
        return bool(inferior_to_uid1 & downstream_of_uid2)

    def _is_inferior_upstream(self, uid1: str, uid2: str) -> bool:
        """Is a task inferior to uid1 upstream of uid2."""
        inferior_to_uid1 = set(self._task_hierarchy.descendants(node=uid1))
        downstream_of_uid2 = set(self.upstream_tasks(uid=uid2))
        return bool(inferior_to_uid1 & downstream_of_uid2)

    def set_priority(self, uid: str, priority: Priority) -> None:
        # TODO: Only requires task_attributes_map & task_hierarchy, not task_dependencies. Consider making a new class, or using a function.
        try:
            attributes = self._task_attributes_map[uid]
        except KeyError as e:
            raise TaskDoesNotExistError(uid=uid) from e

        # Don't need to search if task already has a priority
        if not attributes.priority and self._do_any_superior_tasks_have_priority(
            uid=uid
        ):
            raise SuperiorTaskPrioritiesError(
                uid=uid,
                task_attributes_map=self._task_attributes_map,
                task_hierarchy=self._task_hierarchy,
            )

        attributes.priority = priority

    def set_due_datetime(self, uid: str, due_datetime: datetime.datetime) -> None:
        try:
            attributes = self._task_attributes_map[uid]
        except KeyError as e:
            raise TaskDoesNotExistError(uid=uid) from e

        current_start_datetime = attributes.start_datetime
        if current_start_datetime and due_datetime <= current_start_datetime:
            raise BeforeStartDatetimeError(
                start_datetime=current_start_datetime, due_datetime=due_datetime
            )

        # If a due date is set and the new due date is later than the current
        # due date, there will never be a problem
        current_due_datetime = attributes.due_datetime
        if not current_due_datetime or due_datetime < current_due_datetime:
            # Latest start date of upstream tasks & superior tasks
            pass

        attributes.due_datetime = due_datetime

    def set_start_datetime(self, uid: str, start_datetime: datetime.datetime) -> None:
        try:
            attributes = self._task_attributes_map[uid]
        except KeyError as e:
            raise TaskDoesNotExistError(uid=uid) from e

        current_due_datetime = attributes.due_datetime
        if current_due_datetime and start_datetime >= current_due_datetime:
            raise AfterDueDatetimeError(
                start_datetime=start_datetime, due_datetime=current_due_datetime
            )

        # If a start date is set and the new start date is earlier than the
        # current start date, there will never be a problem
        current_start_datetime = attributes.start_datetime
        if not current_start_datetime or start_datetime > current_start_datetime:
            # TODO: Add block for earliest due date of downstream and superior tasks
            pass

        attributes.start_datetime = start_datetime

    def _do_any_superior_tasks_have_priority(self, uid: str) -> bool:
        """Do any of the superior tasks of task [uid] have a priority?"""
        # Assumption is that task [uid] does not have a set priority
        unsearched_tasks = collections.deque(
            self._task_hierarchy.predecessors(node=uid)
        )
        searched_tasks = set()
        while unsearched_tasks:
            task = unsearched_tasks.popleft()
            priority = self._task_attributes_map[task].priority
            if priority:
                return True
            searched_tasks.add(task)
            for supertask in self._task_hierarchy.predecessors(node=task):
                if supertask not in searched_tasks:
                    unsearched_tasks.append(supertask)

        return False

    def _do_any_inferior_tasks_have_priority(self, uid: str) -> bool:
        """Do any of the inferior tasks of task [uid] have a priority?"""
        unsearched_tasks = collections.deque(self._task_hierarchy.successors(node=uid))
        searched_tasks = set()
        while unsearched_tasks:
            task = unsearched_tasks.popleft()
            priority = self._task_attributes_map[task].priority
            if priority:
                return True
            searched_tasks.add(task)
            for subtask in self._task_hierarchy.successors(node=task):
                if subtask not in searched_tasks:
                    unsearched_tasks.append(subtask)

        return False
