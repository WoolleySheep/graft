"""Local file data-layer implementation and associated exceptions."""

import enum
import logging
import os
import pathlib
import platform
import shutil
import tempfile
from collections.abc import Callable, Iterable
from typing import Final, override

from graft import app_name, architecture, domain
from graft.domain import tasks
from graft.layers.data.local_files import (
    next_unused_task,
    task_attributes_register,
    task_dependency_graph,
    task_hierarchy_graph,
)
from graft.layers.data.local_files.file_schema_version import FileSchemaVersion

_DATA_DIRECTORY_PATH_ENVIRONMENT_VARIABLE_KEY: Final = (
    f"{app_name.APP_NAME}_DATA_DIRECTORY_PATH"
)

_FIRST_TASK: Final = tasks.UID(1)

_DEFAULT_DATA_DIRECTORY_NAME: Final = "data"

_ENCODED_FILE_SCHEMA_VERSION_1: Final = "1"

logger: Final = logging.getLogger(__name__)


class OperatingSystem(enum.Enum):
    WINDOWS = "Windows"


def _encode_version(version: FileSchemaVersion) -> str:
    match version:
        case FileSchemaVersion.V1:
            return _ENCODED_FILE_SCHEMA_VERSION_1


def _decode_version(text: str) -> FileSchemaVersion:
    if text == _ENCODED_FILE_SCHEMA_VERSION_1:
        return FileSchemaVersion.V1

    raise ValueError(f"Unknown file schema version: {text}")


def _decode_versioned_file_contents[T](
    contents: str, get_decoder: Callable[[FileSchemaVersion], Callable[[str], T]]
) -> T:
    encoded_version, encoded_object = contents.split("\n", 1)
    version = _decode_version(encoded_version)
    decode = get_decoder(version)
    return decode(encoded_object)


def _load_from_versioned_file[T](
    file: pathlib.Path, get_decoder: Callable[[FileSchemaVersion], Callable[[str], T]]
) -> T:
    """Load data from a file according to the current schema.

    The file should start with the version number on the first line. This is
    used to look up the corresponding decoder. As a result, the file schema can
    change, as long as a corresponding decoder is available.
    """
    contents = file.read_text()
    return _decode_versioned_file_contents(contents, get_decoder)


def _encode_as_versioned_file_contents[T](
    obj: T,
    version: FileSchemaVersion,
    get_encoder: Callable[[FileSchemaVersion], Callable[[T], str]],
) -> str:
    """Encode object as versioned file content.

    The version number is located on the first line. The object is encoded as a
    string and stored on the second line onwards.
    """
    encoded_version = _encode_version(version)
    encode = get_encoder(version)
    encoded_obj = encode(obj)
    return f"{encoded_version}\n{encoded_obj}\n"


def _get_operating_system() -> OperatingSystem:
    operating_system = platform.system()
    match operating_system:
        case "Windows":
            return OperatingSystem.WINDOWS
        case _:
            # TODO: Add Linux and Max support
            # TODO: Raise proper exception
            raise ValueError(f"OS [{operating_system}] and not currently supported")


def _get_default_data_directory(operating_system: OperatingSystem) -> pathlib.Path:
    match operating_system:
        case OperatingSystem.WINDOWS:
            return (
                pathlib.Path(os.environ["LOCALAPPDATA"])
                / app_name.APP_NAME
                / _DEFAULT_DATA_DIRECTORY_NAME
            )


def _get_data_directory() -> pathlib.Path:
    """Get the directory where system data is stored.

    Will return the directory specified by the environment variable if
    available, otherwise will fall back on defaults for standard OS's.
    """
    if _DATA_DIRECTORY_PATH_ENVIRONMENT_VARIABLE_KEY in os.environ:
        return pathlib.Path(os.environ[_DATA_DIRECTORY_PATH_ENVIRONMENT_VARIABLE_KEY])

    return _get_default_data_directory(_get_operating_system())


class PartiallyInitialisedError(Exception):
    """Exception raised when a data-layer is partially initialised."""


def _save_file_group_atomically(
    files_with_text: Iterable[tuple[pathlib.Path, str]],
) -> None:
    """Write to a group of files atomically, changing no files if any fail.

    Will break if a file is included twice.
    """
    file_pairs = list[tuple[pathlib.Path, pathlib.Path]]()
    try:
        for file, contents in files_with_text:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=file.suffix, dir=file.parent, delete=False
            ) as temp_file:
                file_pairs.append((file, pathlib.Path(temp_file.name)))
                temp_file.write(contents)
    except Exception:
        for _, temp_file in file_pairs:
            pathlib.Path(temp_file).unlink()

    # Replace command is an atomic operation that cannot fail, given the
    # files are in the same directory
    for file, temp_file in file_pairs:
        temp_file.replace(file)


def _next_task_uid(uid: tasks.UID) -> tasks.UID:
    """Get the next task UID."""
    return tasks.UID(int(uid) + 1)


def _generate_next_unused_task(current_unused_task: tasks.UID) -> tasks.UID:
    return _next_task_uid(uid=current_unused_task)


class LocalFilesStatus(enum.Enum):
    """Initialisation status of the local filesystem."""

    NOT_PRESENT = "not initialised"
    SOME_PRESENT = "partially initialised"
    ALL_PRESENT = "fully initialised"


class LocalFilesDataLayer(architecture.DataLayer):
    """Local Files data layer.

    Implementation of the data-layer interface that stores and retrieves data
    from files on the local filesystem.
    """

    def __init__(self) -> None:
        """Initialise LocalFileDataLayer.

        If the filesystem has not been initialised, will do so automatically.
        """
        logger.info("Initialising %s", self.__class__.__name__)
        self._data_directory = _get_data_directory()

        match self._get_local_files_status():
            case LocalFilesStatus.NOT_PRESENT:
                logger.info("Local files not present, creating new local files")
                self._create_new_data_files()
            case LocalFilesStatus.SOME_PRESENT:
                logger.error("Some local files present, cannot proceed in this state")
                raise PartiallyInitialisedError
            case LocalFilesStatus.ALL_PRESENT:
                pass

    @property
    def _task_attributes_register_file(self) -> pathlib.Path:
        return self._data_directory / task_attributes_register.FILENAME

    @property
    def _task_hierarchy_graph_file(self) -> pathlib.Path:
        return self._data_directory / task_hierarchy_graph.FILENAME

    @property
    def _task_dependency_graph_file(self) -> pathlib.Path:
        return self._data_directory / task_dependency_graph.FILENAME

    @property
    def _next_unused_task_file(self) -> pathlib.Path:
        return self._data_directory / next_unused_task.FILENAME

    def _get_local_files_status(self) -> LocalFilesStatus:
        """Get the initialisation status of the local filesystem."""
        if not self._data_directory.exists():
            return LocalFilesStatus.NOT_PRESENT

        return (
            LocalFilesStatus.ALL_PRESENT
            if (
                self._task_attributes_register_file.exists()
                and self._task_hierarchy_graph_file.exists()
                and self._task_dependency_graph_file.exists()
                and self._next_unused_task_file.exists()
            )
            else LocalFilesStatus.SOME_PRESENT
        )

    @override
    def load_next_unused_task(self) -> tasks.UID:
        """Load the next unused task ID.

        "Unused" means that the UID has never been used in the system before,
        regardless of whether the task had subsequently been deleted.

        Loading an unused task UID will not add it to the system, and will
        return the same value if called multiple times. The returned value will
        only change save_system_and_indicate_task_used is called with it.
        """
        return _load_from_versioned_file(
            self._next_unused_task_file, next_unused_task.get_decoder
        )

    def _load_task_system(self) -> tasks.System:
        attributes_register = self._load_task_attributes_register()
        network_graph = self._load_task_network_graph()
        return tasks.System(
            attributes_register=attributes_register,
            network_graph=network_graph,
        )

    def _load_task_attributes_register(self) -> tasks.AttributesRegister:
        return _load_from_versioned_file(
            file=self._task_attributes_register_file,
            get_decoder=task_attributes_register.get_decoder,
        )

    def _load_task_hierarchy_graph(self) -> tasks.HierarchyGraph:
        """Load the task hierarchy graph."""
        return _load_from_versioned_file(
            file=self._task_hierarchy_graph_file,
            get_decoder=task_hierarchy_graph.get_decoder,
        )

    def _load_task_dependency_graph(self) -> tasks.DependencyGraph:
        """Load the task dependency graph."""
        return _load_from_versioned_file(
            file=self._task_dependency_graph_file,
            get_decoder=task_dependency_graph.get_decoder,
        )

    def _load_task_network_graph(self) -> tasks.NetworkGraph:
        """Load the task network graph."""
        dependency_graph = self._load_task_dependency_graph()
        hierearchy_graph = self._load_task_hierarchy_graph()
        return tasks.NetworkGraph(
            dependency_graph=dependency_graph, hierarchy_graph=hierearchy_graph
        )

    @override
    def load_system(self) -> domain.System:
        task_system = self._load_task_system()
        return domain.System(task_system=task_system)

    def _create_new_data_files(self) -> None:
        self._data_directory.mkdir(parents=True)
        self._save_data(system=domain.System.empty(), unused_task=_FIRST_TASK)

    @override
    def erase(self) -> None:
        shutil.rmtree(self._data_directory)
        self._create_new_data_files()

    @override
    def save_system(self, system: domain.ISystemView) -> None:
        self._save_data(system=system)

    @override
    def save_system_and_indicate_task_used(
        self, system: domain.ISystemView, used_task: tasks.UID
    ) -> None:
        current_unused_task = self.load_next_unused_task()

        if used_task != current_unused_task:
            # TODO: Add better Exception
            raise ValueError("Cannot save system with a different unused task UID")

        new_unused_task = _generate_next_unused_task(
            current_unused_task=current_unused_task
        )
        self._save_data(system=system, unused_task=new_unused_task)

    def _save_data(
        self, system: domain.ISystemView, unused_task: tasks.UID | None = None
    ) -> None:
        """Save the system and update the unused task file if necessary."""
        encoded_task_hierarchy_graph = _encode_as_versioned_file_contents(
            obj=system.task_system().network_graph().hierarchy_graph(),
            version=task_hierarchy_graph.CURRENT_VERSION,
            get_encoder=task_hierarchy_graph.get_encoder,
        )
        encoded_task_dependency_graph = _encode_as_versioned_file_contents(
            obj=system.task_system().network_graph().dependency_graph(),
            version=task_dependency_graph.CURRENT_VERSION,
            get_encoder=task_dependency_graph.get_encoder,
        )
        encoded_task_attributes_register = _encode_as_versioned_file_contents(
            obj=system.task_system().attributes_register(),
            version=task_attributes_register.CURRENT_VERSION,
            get_encoder=task_attributes_register.get_encoder,
        )

        files_with_text = [
            (self._task_hierarchy_graph_file, encoded_task_hierarchy_graph),
            (self._task_dependency_graph_file, encoded_task_dependency_graph),
            (self._task_attributes_register_file, encoded_task_attributes_register),
        ]

        if unused_task is not None:
            encoded_unused_task = _encode_as_versioned_file_contents(
                unused_task,
                next_unused_task.CURRENT_VERSION,
                next_unused_task.get_encoder,
            )
            files_with_text.append((self._next_unused_task_file, encoded_unused_task))

        _save_file_group_atomically(files_with_text=files_with_text)
