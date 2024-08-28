from typing import Final

from graft.local_file.decoder import DecodeAttributesRegisterFn
from graft.local_file.encoder import EncodeAttributesRegisterFn
from graft.local_file.file_schema_version import FileSchemaVersion
from graft.local_file.task_attributes_register import v1

FILENAME: Final = "task_attributes_register.txt"

CURRENT_VERSION: Final = FileSchemaVersion.V1


def get_encoder(version: FileSchemaVersion) -> EncodeAttributesRegisterFn:
    match version:
        case FileSchemaVersion.V1:
            return v1.encode_attributes_register

    raise ValueError(f"Unsupported schema version: {version}")


def get_decoder(version: FileSchemaVersion) -> DecodeAttributesRegisterFn:
    match version:
        case FileSchemaVersion.V1:
            return v1.decode_attributes_register

    raise ValueError(f"Unsupported schema version: {version}")
