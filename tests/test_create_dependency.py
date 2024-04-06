import copy
from unittest import mock

import pytest

from graft import domain
from graft.domain import tasks
from graft.standard import standard


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_success(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_dependency method succeeds as expected."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)

    system = empty_system
    system.add_task(dependee_task)
    system.add_task(dependent_task)

    system_with_dependency = copy.deepcopy(system)
    system_with_dependency.add_dependency(
        dependee_task=dependee_task, dependent_task=dependent_task
    )

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.create_dependency(
        dependee_task=dependee_task, dependent_task=dependent_task
    )

    data_layer_mock.load_system.assert_called_once()
    data_layer_mock.save_system.assert_called_once_with(system_with_dependency)


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependee_task_not_exist(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_dependency method fails when the dependee task does not exist."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)
    absent_dependee_task = tasks.UID(2)

    system = empty_system
    system.add_task(dependee_task)
    system.add_task(dependent_task)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.TaskDoesNotExistError) as exc_info:
        logic_layer.create_dependency(
            dependee_task=absent_dependee_task, dependent_task=dependent_task
        )
    assert exc_info.value.task == absent_dependee_task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependent_task_not_exist(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_dependency method fails when the dependent task does not exist."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)
    absent_dependent_task = tasks.UID(2)

    system = empty_system
    system.add_task(dependee_task)
    system.add_task(dependent_task)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.TaskDoesNotExistError) as exc_info:
        logic_layer.create_dependency(
            dependee_task=dependee_task, dependent_task=absent_dependent_task
        )
    assert exc_info.value.task == absent_dependent_task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependent_task_dependee_task_the_same(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_dependency method fails when the dependent task and the dependee task are the same."""
    task = tasks.UID(0)

    system = empty_system
    system.add_task(task)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyLoopError) as exc_info:
        logic_layer.create_dependency(dependee_task=task, dependent_task=task)
    assert exc_info.value.task == task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_dependency_already_exists(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_dependency method fails when the dependency already exists."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)

    system = empty_system
    system.add_task(dependee_task)
    system.add_task(dependent_task)
    system.add_dependency(dependee_task=dependee_task, dependent_task=dependent_task)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyAlreadyExistsError) as exc_info:
        logic_layer.create_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )
    assert exc_info.value.dependee_task == dependee_task
    assert exc_info.value.dependent_task == dependent_task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_inverse_hierarchy_already_exists(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_dependency method fails when the inverse hierarchy already exists."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)

    system = empty_system
    system.add_task(dependee_task)
    system.add_task(dependent_task)
    system.add_dependency(dependee_task=dependee_task, dependent_task=dependent_task)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.InverseDependencyAlreadyExistsError) as exc_info:
        logic_layer.create_dependency(
            dependee_task=dependent_task, dependent_task=dependee_task
        )
    assert exc_info.value.dependee_task == dependee_task
    assert exc_info.value.dependent_task == dependent_task

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_introduces_cycle(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_dependency method fails when the dependency introduces a cycle."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_dependency(dependee_task=task0, dependent_task=task1)
    system.add_dependency(dependee_task=task1, dependent_task=task2)

    expected_subgraph = tasks.DependencyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_dependency(dependee_task=task0, dependent_task=task1)
    expected_subgraph.add_dependency(dependee_task=task1, dependent_task=task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyIntroducesCycleError) as exc_info:
        logic_layer.create_dependency(dependee_task=task2, dependent_task=task0)
    assert exc_info.value.dependee_task == task2
    assert exc_info.value.dependent_task == task0
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_introduces_cycle_prunes_subgraph_correctly(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_dependency method fails when the dependency introduces a cycle and prunes the subgraph correctly."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_dependency(dependee_task=task0, dependent_task=task1)
    system.add_dependency(dependee_task=task1, dependent_task=task2)
    system.add_dependency(dependee_task=task1, dependent_task=task3)

    expected_subgraph = tasks.DependencyGraph()
    expected_subgraph.add_task(task0)
    expected_subgraph.add_task(task1)
    expected_subgraph.add_task(task2)
    expected_subgraph.add_dependency(task0, task1)
    expected_subgraph.add_dependency(task1, task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyIntroducesCycleError) as exc_info:
        logic_layer.create_dependency(dependee_task=task2, dependent_task=task0)
    assert exc_info.value.dependee_task == task2
    assert exc_info.value.dependent_task == task0
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_success_multiple_paths_allowed(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_dependency method succeeds even when there are multiple paths.

    This is different from the hierarchy graph, which does not allow multiple
    paths.
    """
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_dependency(dependee_task=task0, dependent_task=task1)
    system.add_dependency(dependee_task=task1, dependent_task=task2)

    system_with_multiple_paths = copy.deepcopy(system)
    system_with_multiple_paths.add_dependency(dependee_task=task0, dependent_task=task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    logic_layer.create_dependency(dependee_task=task0, dependent_task=task2)

    data_layer_mock.load_system.assert_called_once()
    data_layer_mock.save_system.assert_called_once_with(system_with_multiple_paths)


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_hierarchy_path_from_dependee_task_to_dependent_task(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_dependency method fails when a hierarchy path already exists from the dependee-task to the dependent-task."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)

    system = empty_system
    system.add_task(dependee_task)
    system.add_task(dependent_task)
    system.add_hierarchy(supertask=dependee_task, subtask=dependent_task)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(dependee_task)
    expected_subgraph.add_task(dependent_task)
    expected_subgraph.add_hierarchy(dependee_task, dependent_task)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.HierarchyPathAlreadyExistsFromDependeeTaskToDependentTaskError
    ) as exc_info:
        logic_layer.create_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )
    assert exc_info.value.dependee_task == dependee_task
    assert exc_info.value.dependent_task == dependent_task
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_hierarchy_path_from_dependent_task_to_dependee_task(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_dependency method fails when a hierarchy path already exists from the dependent-task to the dependee-task."""
    dependee_task = tasks.UID(0)
    dependent_task = tasks.UID(1)

    system = empty_system
    system.add_task(dependee_task)
    system.add_task(dependent_task)
    system.add_hierarchy(supertask=dependent_task, subtask=dependee_task)

    expected_subgraph = tasks.HierarchyGraph()
    expected_subgraph.add_task(dependee_task)
    expected_subgraph.add_task(dependent_task)
    expected_subgraph.add_hierarchy(dependent_task, dependee_task)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.HierarchyPathAlreadyExistsFromDependentTaskToDependeeTaskError
    ) as exc_info:
        logic_layer.create_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )
    assert exc_info.value.dependee_task == dependee_task
    assert exc_info.value.dependent_task == dependent_task
    assert exc_info.value.connecting_subgraph == expected_subgraph

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_introduces_stream_cycle(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_dependency method fails when a stream cycle is introduced."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)

    system.add_dependency(task0, task1)
    system.add_hierarchy(task1, task2)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyIntroducesStreamCycleError) as exc_info:
        logic_layer.create_dependency(task2, task0)
    assert exc_info.value.dependee_task == task2
    assert exc_info.value.dependent_task == task0

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_path_from_inferior_task_of_dependent_task_to_dependee_task(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_dependency method fails when a stream path already exists from an inferior task of the dependent-task to the dependee-task."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)
    task4 = tasks.UID(4)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)

    system.add_hierarchy(task0, task1)
    system.add_dependency(task1, task2)
    system.add_dependency(task2, task3)
    system.add_hierarchy(task3, task4)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.StreamPathFromInferiorTaskOfDependentTaskToDependeeTaskExistsError
    ) as exc_info:
        logic_layer.create_dependency(task4, task0)
    assert exc_info.value.dependee_task == task4
    assert exc_info.value.dependent_task == task0

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_path_from_dependent_task_to_inferior_task_of_dependee_task(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_dependency method fails when a stream path already exists from the dependent-task to an inferior task of the dependee-task."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)
    task4 = tasks.UID(4)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)

    system.add_dependency(task0, task1)
    system.add_hierarchy(task1, task2)
    system.add_dependency(task2, task3)
    system.add_hierarchy(task4, task3)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(
        tasks.StreamPathFromDependentTaskToInferiorTaskOfDependeeTaskExistsError
    ) as exc_info:
        logic_layer.create_dependency(task4, task0)
    assert exc_info.value.dependee_task == task4
    assert exc_info.value.dependent_task == task0

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False


@mock.patch("graft.architecture.data.DataLayer", autospec=True)
def test_create_dependency_failure_introduces_hierarchy_clash(
    data_layer_mock: mock.MagicMock, empty_system: domain.System
) -> None:
    """Test the create_dependency method fails when a hierarchy clash is introduced."""
    task0 = tasks.UID(0)
    task1 = tasks.UID(1)
    task2 = tasks.UID(2)
    task3 = tasks.UID(3)

    system = empty_system
    system.add_task(task0)
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)

    system.add_hierarchy(task0, task1)
    system.add_hierarchy(task2, task3)
    system.add_dependency(task1, task3)

    data_layer_mock.load_system.return_value = system

    logic_layer = standard.StandardLogicLayer(data_layer=data_layer_mock)

    with pytest.raises(tasks.DependencyIntroducesHierarchyClashError) as exc_info:
        logic_layer.create_dependency(task0, task2)
    assert exc_info.value.dependee_task == task0
    assert exc_info.value.dependent_task == task2

    data_layer_mock.load_system.assert_called_once()
    assert data_layer_mock.save_system.called is False
