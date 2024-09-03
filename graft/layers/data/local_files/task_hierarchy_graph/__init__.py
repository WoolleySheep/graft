from typing import Final

from graft.layers.data.local_files.decoder import DecodeHierarchyGraphFn
from graft.layers.data.local_files.encoder import EncodeHierarchyGraphFn
from graft.layers.data.local_files.file_schema_version import FileSchemaVersion
from graft.layers.data.local_files.task_hierarchy_graph import v1

FILENAME: Final = "task_hierarchy_graph.txt"

CURRENT_VERSION: Final = FileSchemaVersion.V1


def get_encoder(version: FileSchemaVersion) -> EncodeHierarchyGraphFn:
    match version:
        case FileSchemaVersion.V1:
            return v1.encode_hierarchy_graph

    raise ValueError(f"Unsupported schema version: {version}")


def get_decoder(version: FileSchemaVersion) -> DecodeHierarchyGraphFn:
    match version:
        case FileSchemaVersion.V1:
            return v1.decode_hierarchy_graph

    raise ValueError(f"Unsupported schema version: {version}")
