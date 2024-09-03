from typing import Final

from graft.layers.data.local_files.decoder import DecodeNextUnusedTaskFn
from graft.layers.data.local_files.encoder import EncodeNextUnusedTaskFn
from graft.layers.data.local_files.file_schema_version import FileSchemaVersion
from graft.layers.data.local_files.next_unused_task import v1

FILENAME: Final = "next_unused_task.txt"

CURRENT_VERSION: Final = FileSchemaVersion.V1


def get_encoder(version: FileSchemaVersion) -> EncodeNextUnusedTaskFn:
    match version:
        case FileSchemaVersion.V1:
            return v1.encode_next_unused_task

    raise ValueError(f"Unsupported schema version: {version}")


def get_decoder(version: FileSchemaVersion) -> DecodeNextUnusedTaskFn:
    match version:
        case FileSchemaVersion.V1:
            return v1.decode_next_unused_task

    raise ValueError(f"Unsupported schema version: {version}")
