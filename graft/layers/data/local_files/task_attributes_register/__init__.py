from typing import Final

from graft.layers.data.local_files.decoder import DecodeAttributesRegisterFn
from graft.layers.data.local_files.encoder import EncodeAttributesRegisterFn
from graft.layers.data.local_files.file_schema_version import FileSchemaVersion
from graft.layers.data.local_files.task_attributes_register import v1

FILENAME: Final = "task_attributes_register.txt"

CURRENT_VERSION: Final = FileSchemaVersion.V1


def get_encoder(version: FileSchemaVersion) -> EncodeAttributesRegisterFn:
    match version:
        case FileSchemaVersion.V1:
            return v1.encode_attributes_register

    msg = f"Unsupported schema version: {version}"
    raise ValueError(msg)


def get_decoder(version: FileSchemaVersion) -> DecodeAttributesRegisterFn:
    match version:
        case FileSchemaVersion.V1:
            return v1.decode_attributes_register

    msg = f"Unsupported schema version: {version}"
    raise ValueError(msg)
