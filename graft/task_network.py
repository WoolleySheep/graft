import collections
from typing import Collection, Hashable, Mapping, MutableMapping

import networkx as nx

from graft.constrained_graph import (
    ConstrainedGraph,
    EdgeDoesNotExistError,
    NodeDoesNotExistError,
    NoTargetPredecessorsAsSourceAncestorsError,
    NotReachableError,
    SelfLoopError,
)
from graft.priority import Priority
from graft.task_attributes import TaskAttributes


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


class Dependent2TaskError(Exception):
    def __init__(self, uid1: str, uid2: str, digraph: nx.DiGraph, *args, **kwargs):
        self.uid1 = uid1
        self.uid2 = uid2
        self.digraph = digraph

        # TODO: Add Error message
        super().__init__("", *args, **kwargs)


class Dependee2TasksError(Exception):
    def __init__(self, uid1: str, uid2: str, superior_tasks: set[str], *args, **kwargs):
        self.uid1 = uid1
        self.uid2 = uid2
        self.superior_tasks = superior_tasks

        # TODO: Add Error message
        super().__init__("", *args, **kwargs)


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
        task_dependencies: ConstrainedGraph,
    ) -> None:
        self._task_attributes_map = task_attributes_map
        self._task_hierarchy = task_hierarchy
        self._task_dependencies = task_dependencies

    def add_task(self, uid: str) -> None:
        """Add a task to the network."""
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
            dependent2_check_digraph = self._task_dependencies.get_joining_subgraph(
                source=uid1, target=uid2
            )
        except NotReachableError:
            pass
        else:
            raise Dependent2TaskError(
                uid1=uid1, uid2=uid2, digraph=dependent2_check_digraph
            )

        try:
            dependee2_tasks = self._task_dependencies.get_target_predecessors_that_are_source_ancestors(
                source=uid1, target=uid2
            )
        except NoTargetPredecessorsAsSourceAncestorsError:
            pass
        else:
            raise Dependee2TasksError(
                uid1=uid1, uid2=uid2, superior_tasks=dependee2_tasks
            )

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

    def set_priority(self, uid: str, priority: Priority) -> None:
        # TODO: Only requires task_attributes_map & task_hierarchy, not task_dependencies. Consider making a new class, or using a function.
        try:
            attributes = self.task_attributes_map[uid]
        except KeyError as e:
            raise TaskDoesNotExistError(uid=uid) from e

        # Don't need to search if task already has a priority
        if not attributes.priority and self._do_any_superior_tasks_have_priority(
            uid=uid
        ):
            raise SuperiorTaskPrioritiesError(
                uid=uid,
                task_attributes_map=self.task_attributes_map,
                task_hierarchy=self.task_hierarchy,
            )

        attributes.priority = priority

    def _do_any_superior_tasks_have_priority(self, uid: str) -> bool:
        """Do any of the superior tasks of task [uid] have a priority?"""
        # Assumption is that task [uid] does not have a set priority
        unsearched_tasks = collections.deque(self.task_hierarchy.predecessors(node=uid))
        searched_tasks = set()
        while unsearched_tasks:
            task = unsearched_tasks.popleft()
            priority = self.task_attributes_map[task].priority
            if priority:
                return True
            searched_tasks.add(task)
            for supertask in self.task_hierarchy.predecessors(node=task):
                if supertask not in searched_tasks:
                    unsearched_tasks.append(supertask)

        return False
