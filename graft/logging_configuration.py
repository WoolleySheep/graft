import enum
import logging
import os
import pathlib
import platform
from logging import handlers
from typing import Final

from graft import app_name

_LOG_DIRECTORY_PATH_ENVIRONMENT_VARIABLE_KEY: Final = (
    f"{app_name.APP_NAME}_LOG_DIRECTORY_PATH"
)

_LOGGING_LEVEL_ENVIRONMENT_VARIABLE_KEY: Final = f"{app_name.APP_NAME}_LOGGING_LEVEL"
_LOGGING_LEVEL_ENVIRONMENT_VARIABLE_DEBUG_VALUE: Final = "DEBUG"
_LOGGING_LEVEL_ENVIRONMENT_VARIABLE_INFO_VALUE: Final = "INFO"
_LOGGING_LEVEL_ENVIRONMENT_VARIABLE_WARNING_VALUE: Final = "WARNING"
_LOGGING_LEVEL_ENVIRONMENT_VARIABLE_ERROR_VALUE: Final = "ERROR"
_LOGGING_LEVEL_ENVIRONMENT_VARIABLE_CRITICAL_VALUE: Final = "CRITICAL"

_DEFAULT_LOG_DIRECTORY_NAME: Final = "logs"

_DEFAULT_LOGGING_LEVEL: Final = logging.INFO

_DEVELOPER_LOG_FILE_NAME: Final = "developer.log"
_DEVELOPER_LOG_FILE_MAX_SIZE_BYTES: Final = 10 * 1024 * 1024
_DEVELOPER_LOG_FILE_NUMBER_OF_BACKUPS: Final = 1
_DEVELOPER_LOG_FILE_LOG_FORMAT: Final = (
    "%(asctime)s %(levelname)s:%(filename)s %(message)s"
)
_DEVELOPER_LOG_FILE_LOG_DATE_FORMAT: Final = "%Y-%m-%dT%H:%M:%S"


class OperatingSystem(enum.Enum):
    WINDOWS = enum.auto()


def _parse_level_from_environment_variable_value(level: str) -> int:
    if level == _LOGGING_LEVEL_ENVIRONMENT_VARIABLE_DEBUG_VALUE:
        return logging.DEBUG

    if level == _LOGGING_LEVEL_ENVIRONMENT_VARIABLE_INFO_VALUE:
        return logging.INFO

    if level == _LOGGING_LEVEL_ENVIRONMENT_VARIABLE_WARNING_VALUE:
        return logging.WARNING

    if level == _LOGGING_LEVEL_ENVIRONMENT_VARIABLE_ERROR_VALUE:
        return logging.ERROR

    if level == _LOGGING_LEVEL_ENVIRONMENT_VARIABLE_CRITICAL_VALUE:
        return logging.CRITICAL

    msg = f"Unknown logging level: {level}"
    raise ValueError(msg)


def _get_level() -> int:
    if _LOGGING_LEVEL_ENVIRONMENT_VARIABLE_KEY in os.environ:
        formatted_level = os.environ[_LOGGING_LEVEL_ENVIRONMENT_VARIABLE_KEY]
        return _parse_level_from_environment_variable_value(formatted_level)

    return _DEFAULT_LOGGING_LEVEL


def _silence_annoying_matplotlib_logging() -> None:
    r"""Stop matplotlib spamming DEBUG level logs that clutter up my files.

    This is the sort of stuff they were throwing out:
    - DEBUG:pyplot.py Loaded backend Agg version v2.2.
    - DEBUG:font_manager.py findfont: Matching sans\-serif:style=normal:variant=normal:weight=normal:stretch=normal:size=10.0.
    - DEBUG:font_manager.py findfont: score(FontEntry(fname=<PATH_TO_DEPENDENCIES>mpl-data\\fonts\\ttf\\DejaVuSerif-Bold.ttf', name='DejaVu Serif', style='normal', variant='normal', weight=700, stretch='normal', size='scalable')) = 10.335
    """
    # It's hacky, but it'll do
    logging.getLogger("matplotlib.font_manager").setLevel(logging.INFO)
    logging.getLogger("matplotlib.pyplot").setLevel(logging.INFO)


def _get_operating_system() -> OperatingSystem:
    operating_system = platform.system()
    match operating_system:
        case "Windows":
            return OperatingSystem.WINDOWS
        case _:
            # TODO: Add Linux and Mac support
            # TODO: Raise proper exception
            msg = f"OS [{operating_system}] not currently supported"
            raise ValueError(msg)


def _get_default_log_directory(operating_system: OperatingSystem) -> pathlib.Path:
    match operating_system:
        case OperatingSystem.WINDOWS:
            return (
                pathlib.Path(os.environ["LOCALAPPDATA"])
                / app_name.APP_NAME
                / _DEFAULT_LOG_DIRECTORY_NAME
            )


def _get_log_directory() -> pathlib.Path:
    """Get the directory where app logs are stored.

    Will return the directory specified by the environment variable if
    available, otherwise will fall back on defaults for standard OS's.
    """
    if _LOG_DIRECTORY_PATH_ENVIRONMENT_VARIABLE_KEY in os.environ:
        return pathlib.Path(os.environ[_LOG_DIRECTORY_PATH_ENVIRONMENT_VARIABLE_KEY])

    return _get_default_log_directory(_get_operating_system())


def _create_log_directory() -> None:
    log_directory = _get_log_directory()
    log_directory.mkdir(parents=True, exist_ok=True)


def _create_rotating_developer_log_files_handler() -> handlers.RotatingFileHandler:
    handler = handlers.RotatingFileHandler(
        _get_log_directory() / _DEVELOPER_LOG_FILE_NAME,
        maxBytes=_DEVELOPER_LOG_FILE_MAX_SIZE_BYTES,
        backupCount=_DEVELOPER_LOG_FILE_NUMBER_OF_BACKUPS,
    )
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt=_DEVELOPER_LOG_FILE_LOG_FORMAT, datefmt=_DEVELOPER_LOG_FILE_LOG_DATE_FORMAT
    )
    handler.setFormatter(formatter)

    return handler


def configure_logging() -> None:
    """Configure logging for the graft application."""
    _silence_annoying_matplotlib_logging()

    level = _get_level()

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    _create_log_directory()

    developer_log_handler = _create_rotating_developer_log_files_handler()
    root_logger.addHandler(developer_log_handler)
