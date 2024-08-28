from typing import Final

from graft.local_file.decoder import DecodeDependencyGraphFn
from graft.local_file.encoder import EncodeDependencyGraphFn
from graft.local_file.file_schema_version import FileSchemaVersion
from graft.local_file.task_dependency_graph import v1

FILENAME: Final = "task_dependency_graph.txt"

CURRENT_VERSION: Final = FileSchemaVersion.V1


def get_encoder(version: FileSchemaVersion) -> EncodeDependencyGraphFn:
    match version:
        case FileSchemaVersion.V1:
            return v1.encode_dependency_graph

    raise ValueError(f"Unsupported schema version: {version}")


def get_decoder(version: FileSchemaVersion) -> DecodeDependencyGraphFn:
    match version:
        case FileSchemaVersion.V1:
            return v1.decode_dependency_graph

    raise ValueError(f"Unsupported schema version: {version}")
