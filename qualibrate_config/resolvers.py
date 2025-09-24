import logging
import os
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import TypeVar

import jsonpointer

from qualibrate_config.cli import migrate_command
from qualibrate_config.file import get_config_file, read_config_file
from qualibrate_config.models import BaseConfig, QualibrateConfig
from qualibrate_config.models.qualibrate import QualibrateTopLevelConfig
from qualibrate_config.qulibrate_types import RawConfigType
from qualibrate_config.validation import (
    GreaterThanSupportedQualibrateConfigVersionError,
    InvalidQualibrateConfigVersionError,
    get_config_model_or_print_error,
    qualibrate_version_validator,
)
from qualibrate_config.vars import (
    CONFIG_PATH_ENV_NAME,
    DEFAULT_CONFIG_FILENAME,
    QUALIBRATE_PATH,
)

__all__ = [
    "get_config_dict",
    "get_config_model",
    "get_qualibrate_config_path",
    "get_qualibrate_config",
]

ConfigClass = TypeVar("ConfigClass", bound=BaseConfig)


def get_qualibrate_config_path() -> Path:
    """
    Retrieve the qualibrate configuration file path. If an environment variable
    for the config path is set, it uses that; otherwise, it defaults to the
    standard Qualibrate path.
    """
    return get_config_file(
        os.environ.get(CONFIG_PATH_ENV_NAME, QUALIBRATE_PATH),
        DEFAULT_CONFIG_FILENAME,
        raise_not_exists=False,
    )


def get_config_dict(
    config_path: Path,
    config_key: str | None,
    config: RawConfigType | None = None,
) -> RawConfigType:
    if config is None or config_key is None or config_key not in config:
        config = read_config_file(config_path, solve_references=False)
    if config is None:
        raise RuntimeError("Couldn't read config file")
    if config_key is None:
        return dict(config)
    return dict(config.get(config_key, {}))


def get_config_dict_from_subpath(
    config_path: Path,
    subpath: str | None,
    config: RawConfigType | None = None,
) -> RawConfigType:
    """
    Retrieves a configuration dictionary and optionally resolves a subpath
    within it.

    Args:
        config_path: The path to the configuration file.
        subpath: The optional JSON pointer string indicating the subpath
            within the configuration dictionary to retrieve. If None, the
            entire configuration dictionary is returned.
        config: An optional existing configuration dictionary to use instead
            of reading from the file. Defaults to None.

    Returns:
        A dictionary representing the configuration or the resolved subpath
        within it.
    """
    config_dict = get_config_dict(config_path, None, config)
    if subpath is None:
        return config_dict
    return dict(jsonpointer.resolve_pointer(config_dict, subpath))


def get_config_model(
    config_path: Path,
    config_key: str | None,
    config_class: type[ConfigClass] = QualibrateConfig,  # type: ignore
    config: RawConfigType | None = None,
    raw_config_validators: list[Callable[[RawConfigType], None]] | None = None,
) -> ConfigClass:
    """Retrieve the configuration settings.

        Args:
        config_path: Path to the configuration file.
        config: Optional pre-loaded configuration data. If not provided, it
            will load and resolve references from the config file.

    Returns:
        An instance of QualibrateConfig with the loaded configuration.

    Raises:
        RuntimeError: If the configuration file cannot be read or if the
            configuration state is invalid.
    """
    model_config_dict = get_config_dict(config_path, config_key, config)
    if raw_config_validators:
        for validator in raw_config_validators:
            validator(model_config_dict)
    new_config = get_config_model_or_print_error(
        model_config_dict,
        config_class,
        config_key,
    )
    if new_config is None:
        raise RuntimeError(f"Invalid config {config_class.__name__} state")
    return new_config


def get_qualibrate_config(
    config_path: Path | None = None,
    config: RawConfigType | None = None,
    auto_migrate: bool = True,
) -> QualibrateConfig:
    """Retrieve the Qualibrate configuration.

    Args:
        config_path: Optional pre-loaded configuration data. If not provided, it
            will load and resolve references from the config file.
        config: Optional pre-loaded configuration data. If not provided, it
            will load and resolve references from the config file.
        auto_migrate: is it needed to automatically apply migrations to config

    Returns:
        An instance of QualibrateConfig with the loaded configuration.

    Raises:
        RuntimeError: If the configuration file cannot be read or if the
            configuration state is invalid.
    """
    if config_path is None:
        config_path = get_qualibrate_config_path()

    get_config_model_part = partial(
        get_config_model,
        config_path,
        config_key=None,
        config_class=QualibrateTopLevelConfig,
        config=config,
    )
    common_error_msg = (
        "QUAlibrate was unable to load the config. It is recommend to run "
        '"qualibrate config" to fix any file issues. If this problem persists, '
        f'please delete "{config_path}" and retry running '
        '"qualibrate config"'
    )
    try:
        model = get_config_model_part(
            raw_config_validators=[qualibrate_version_validator]
        )
    except GreaterThanSupportedQualibrateConfigVersionError as ex:
        error_msg = (
            f"QUAlibrate was unable to load the config. {str(ex)}. If this "
            f'problem persists, please delete "{config_path}" and retry '
            'running "qualibrate config"'
        )
        raise RuntimeError(error_msg) from ex
    except InvalidQualibrateConfigVersionError:
        if not auto_migrate:
            raise
        logging.info("Automatically migrate to new qualibrate config")
        migrate_command(["--config-path", config_path], standalone_mode=False)
    except (RuntimeError, ValueError) as ex:
        raise RuntimeError(common_error_msg) from ex
    else:
        return model.qualibrate
    # migrated
    try:
        model = get_config_model_part()
    except (RuntimeError, ValueError) as ex:
        raise RuntimeError(common_error_msg) from ex
    return model.qualibrate


if __name__ == "__main__":
    get_qualibrate_config(get_qualibrate_config_path())
