def test_add_task(task_network):
    assert "1" not in task_network._task_attributes_map
    assert "1" not in task_network._task_hierarchy
    assert "1" not in task_network._task_dependencies

    # When the task is added to the network
    task_network.add_task("1")

    # Then it is added to each of the components
    assert "1" in task_network._task_attributes_map
    assert "1" in task_network._task_hierarchy
    assert "1" in task_network._task_dependencies
