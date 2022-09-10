import csv
import json
from pathlib import Path

import networkx as nx

from graft.constrained_graph import ConstrainedGraph
from graft.task_attributes import TaskAttributes
from graft.task_tag_table import TaskTagTable

NODE_LABEL_DELIMITER = ","

DATA_DIRECTORY = Path("data")

TASK_UID_COUNT_FILEPATH = DATA_DIRECTORY / "task_uid_count.txt"

TASK_HIERARCHY_GRAPH_FILEPATH = DATA_DIRECTORY / "task_hierarchy_graph.txt"
TASK_DEPENDENCY_GRAPH_FILEPATH = DATA_DIRECTORY / "task_dependency_graph.txt"

TAG_HIERARCHY_GRAPH_FILEPATH = DATA_DIRECTORY / "tag_hierarchy_graph.txt"

TASK_ATTRIBUTES_MAP_FILEPATH = DATA_DIRECTORY / "task_attributes_map.json"

TASK_TAG_TABLE_FILEPATH = DATA_DIRECTORY / "task_tag_table.csv"

# TODO: Investigate threaded file loading for improved performance


def save_task_attributes_map(task_attributes_map: dict[str, TaskAttributes]) -> None:
    task_attributes_map_dict = {
        uid: task_attributes.to_json_serializable_dict()
        for uid, task_attributes in task_attributes_map.items()
    }
    task_attributes_map_json = json.dumps(obj=task_attributes_map_dict, indent=4)
    TASK_ATTRIBUTES_MAP_FILEPATH.write_text(data=task_attributes_map_json)


def load_task_attributes_map() -> dict[str, TaskAttributes]:
    task_attributes_map_json = TASK_ATTRIBUTES_MAP_FILEPATH.read_text()
    task_attributes_map_dict = json.loads(task_attributes_map_json)
    task_attributes_map = {
        uid: TaskAttributes.from_json_serializable_dict(task_attributes_dict)
        for uid, task_attributes_dict in task_attributes_map_dict.items()
    }
    return task_attributes_map


def _save_graph_to_file(graph: nx.Graph, filepath: Path) -> None:
    nx.write_adjlist(G=graph, path=filepath, delimiter=NODE_LABEL_DELIMITER)


def _load_constrained_graph_from_file(filepath: Path) -> ConstrainedGraph:
    constrained_graph = nx.read_adjlist(
        path=filepath, create_using=ConstrainedGraph, delimiter=NODE_LABEL_DELIMITER
    )
    constrained_graph.mimic = False
    return constrained_graph


def get_next_task_uid() -> int:
    return int(TASK_UID_COUNT_FILEPATH.read_text()) + 1


def increment_task_uid_count() -> None:
    next_uid = get_next_task_uid()
    TASK_UID_COUNT_FILEPATH.write_text(data=str(next_uid))


def save_tag_hierarchy(tag_hierarchy: nx.Graph) -> None:
    _save_graph_to_file(graph=tag_hierarchy, filepath=TAG_HIERARCHY_GRAPH_FILEPATH)


def load_tag_hierarchy() -> ConstrainedGraph:
    return _load_constrained_graph_from_file(filepath=TAG_HIERARCHY_GRAPH_FILEPATH)


def initialise_tag_hierarchy() -> None:
    save_tag_hierarchy(ConstrainedGraph())


def initialise_task_uid_count() -> None:
    TASK_UID_COUNT_FILEPATH.write_text(data="0")


def load_task_hierarchy() -> ConstrainedGraph:
    return _load_constrained_graph_from_file(filepath=TASK_HIERARCHY_GRAPH_FILEPATH)


def save_task_hierarchy(task_hierarchy: nx.Graph) -> None:
    _save_graph_to_file(graph=task_hierarchy, filepath=TASK_HIERARCHY_GRAPH_FILEPATH)


def load_task_dependencies() -> ConstrainedGraph:
    return _load_constrained_graph_from_file(filepath=TASK_DEPENDENCY_GRAPH_FILEPATH)


def save_task_dependencies(task_dependencies: ConstrainedGraph) -> None:
    _save_graph_to_file(
        graph=task_dependencies, filepath=TASK_DEPENDENCY_GRAPH_FILEPATH
    )


def is_tag_hierarchy_initialised() -> bool:
    return TAG_HIERARCHY_GRAPH_FILEPATH.exists()


def initialise_task_attributes_map() -> None:
    save_task_attributes_map(task_attributes_map={})


def initialise_task_hierarchy() -> None:
    save_task_hierarchy(task_hierarchy=ConstrainedGraph())


def initialise_task_dependencies() -> None:
    save_task_dependencies(task_dependencies=ConstrainedGraph())


def initialise_task_tag_table() -> None:
    save_task_tag_table(table=TaskTagTable())


def save_task_tag_table(table: TaskTagTable) -> None:
    with open(TASK_TAG_TABLE_FILEPATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(table.data)


def load_task_tag_table() -> TaskTagTable:
    with open(TASK_TAG_TABLE_FILEPATH, "r") as f:
        reader = csv.reader(f)
        data = {tuple(row) for row in reader}
    return TaskTagTable(data=data)


def initialise_data_directory() -> None:
    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)


def initialise_all() -> None:
    initialise_data_directory()
    initialise_task_uid_count()
    initialise_task_attributes_map()
    initialise_task_hierarchy()
    initialise_task_dependencies()
    initialise_task_tag_table()
