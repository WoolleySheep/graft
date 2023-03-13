import csv
import json
import pathlib
from pathlib import Path

import networkx as nx

import graft.objects.event as event
import graft.objects.task as task
from graft.objects.event import EventRegister
from graft.objects.event_task_due_table import EventTaskDueTable
from graft.objects.graph import ConstrainedGraph, GraftGraph, TaskHierarchies
from graft.objects.task import TaskRegister

NODE_LABEL_DELIMITER = ","

DATA_DIRECTORY_PATH = (
    pathlib.Path.home() / "Utils" / "graft" / "data"
    if False
    else pathlib.Path.home() / "code" / "Python" / "graft" / "data"
)


TASK_ID_COUNT_FILEPATH = DATA_DIRECTORY_PATH / "task_id_count.txt"
EVENT_ID_COUNT_FILEPATH = DATA_DIRECTORY_PATH / "event_id_count.txt"


TASK_HIERARCHIES_GRAPH_FILEPATH = DATA_DIRECTORY_PATH / "task_hierarchies_graph.txt"
TASK_DEPENDENCIES_GRAPH_FILEPATH = DATA_DIRECTORY_PATH / "task_dependencies_graph.txt"

TASK_REGISTER_FILEPATH = DATA_DIRECTORY_PATH / "task_register.json"

EVENT_REGISTER_FILEPATH = DATA_DIRECTORY_PATH / "event_register.json"

EVENT_TASK_DUE_TABLE_FILEPATH = DATA_DIRECTORY_PATH / "event_task_due_table.csv"


def save_task_register(register: TaskRegister) -> None:
    serialisable = {
        str(id): task.to_serialisable_format() for id, task in register.items()
    }
    formatted = json.dumps(obj=serialisable, indent=4)
    TASK_REGISTER_FILEPATH.write_text(formatted)


def load_task_register() -> TaskRegister:
    formatted = TASK_REGISTER_FILEPATH.read_text()
    serialised = json.loads(formatted)
    id_task_map = {
        task.Id(id): task.Task.from_serialisable_format(serialised_task)
        for id, serialised_task in serialised.items()
    }
    return TaskRegister(id_task_map)


def save_event_register(register: EventRegister) -> None:
    serialisable = {
        str(id): event.to_serialisable_format() for id, event in register.items()
    }
    formatted = json.dumps(obj=serialisable, indent=4)
    EVENT_REGISTER_FILEPATH.write_text(formatted)


def load_event_register() -> EventRegister:
    formatted = EVENT_REGISTER_FILEPATH.read_text()
    serialised = json.loads(formatted)
    id_event_map = {
        event.Id(id): event.Event.from_serialisable_format(serialised_event)
        for id, serialised_event in serialised.items()
    }
    return EventRegister(id_event_map)


def _save_graft_graph(graph: GraftGraph, filepath: Path) -> None:
    nx.write_adjlist(G=graph._digraph, path=filepath, delimiter=NODE_LABEL_DELIMITER)


def _load_constrained_graph(filepath: Path) -> ConstrainedGraph:
    digraph = nx.read_adjlist(
        path=filepath, create_using=nx.DiGraph, delimiter=NODE_LABEL_DELIMITER
    )
    return ConstrainedGraph(digraph=digraph)


def get_next_task_id() -> task.Id:
    current_id = task.Id(int(TASK_ID_COUNT_FILEPATH.read_text()))
    return current_id.next()


def increment_task_id_count() -> None:
    next_id = get_next_task_id()
    TASK_ID_COUNT_FILEPATH.write_text(data=str(next_id))


def initialise_task_id_count() -> None:
    TASK_ID_COUNT_FILEPATH.write_text(data="0")


def get_next_event_id() -> event.Id:
    current_id = event.Id(int(EVENT_ID_COUNT_FILEPATH.read_text()))
    return current_id.next()


def increment_event_id_count() -> None:
    next_id = get_next_event_id()
    EVENT_ID_COUNT_FILEPATH.write_text(data=str(next_id))


def initialise_event_id_count() -> None:
    EVENT_ID_COUNT_FILEPATH.write_text(data="0")


def load_task_hierarchies() -> TaskHierarchies:
    return _load_constrained_graph(filepath=TASK_HIERARCHIES_GRAPH_FILEPATH)


def save_task_hierarchies(task_hierarchies: GraftGraph) -> None:
    _save_graft_graph(graph=task_hierarchies, filepath=TASK_HIERARCHIES_GRAPH_FILEPATH)


def load_task_dependencies() -> ConstrainedGraph:
    return _load_constrained_graph(filepath=TASK_DEPENDENCIES_GRAPH_FILEPATH)


def save_task_dependencies(task_dependencies: GraftGraph) -> None:
    _save_graft_graph(
        graph=task_dependencies, filepath=TASK_DEPENDENCIES_GRAPH_FILEPATH
    )


def save_event_task_due_table(table: EventTaskDueTable) -> None:
    with open(EVENT_TASK_DUE_TABLE_FILEPATH, "w", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerows((str(event_id), str(task_id)) for event_id, task_id in table)


def load_event_task_due_table() -> EventTaskDueTable:
    table = EventTaskDueTable()
    with open(EVENT_TASK_DUE_TABLE_FILEPATH, "r") as fp:
        reader = csv.reader(fp)
        for row in reader:
            event_id, task_id = row
            table.add(event.Id(event_id), task.Id(task_id))
        return table


def initialise_task_register() -> None:
    save_task_register(register=TaskRegister())


def initialise_event_register() -> None:
    save_event_register(register=EventRegister())


def initialise_task_hierarchies() -> None:
    save_task_hierarchies(task_hierarchies=GraftGraph())


def initialise_task_dependencies() -> None:
    save_task_dependencies(task_dependencies=GraftGraph())


def initialise_task_event_due_table() -> None:
    save_event_task_due_table(table=EventTaskDueTable())


def initialise_data_directory() -> None:
    DATA_DIRECTORY_PATH.mkdir(parents=True, exist_ok=True)


def initialise() -> None:
    initialise_data_directory()

    initialise_task_id_count()
    initialise_event_id_count()

    initialise_task_register()
    initialise_task_hierarchies()
    initialise_task_dependencies()

    initialise_event_register()
    initialise_task_event_due_table()
