import os
from pathlib import Path
from typing import Any, Optional, TypeVar, cast

import jsonpointer

from qualibrate_config.file import get_config_file, read_config_file
from qualibrate_config.models import ActiveMachineSettings, QualibrateSettings
from qualibrate_config.models.base.base_referenced_settings import (
    BaseReferencedSettings,
)
from qualibrate_config.validation import (
    get_config_model_or_print_error,
)
from qualibrate_config.vars import (
    ACTIVE_MACHINE_CONFIG_KEY,
    CONFIG_PATH_ENV_NAME,
    DEFAULT_ACTIVE_MACHINE_CONFIG_FILENAME,
    DEFAULT_QUALIBRATE_CONFIG_FILENAME,
    QUALIBRATE_CONFIG_KEY,
    QUALIBRATE_PATH,
)

__all__ = [
    "get_active_machine_config_path",
    "get_active_machine_settings",
    "get_config_dict",
    "get_config_model",
    "get_qualibrate_config_path",
    "get_qualibrate_settings",
]

ConfigModel = TypeVar("ConfigModel", bound=BaseReferencedSettings)


def get_qualibrate_config_path() -> Path:
    """
    Retrieve the qualibrate configuration file path. If an environment variable
    for the config path is set, it uses that; otherwise, it defaults to the
    standard Qualibrate path.
    """
    return get_config_file(
        os.environ.get(CONFIG_PATH_ENV_NAME, QUALIBRATE_PATH),
        DEFAULT_QUALIBRATE_CONFIG_FILENAME,
        raise_not_exists=False,
    )


def get_active_machine_config_path() -> Path:
    """
    Retrieve the active machine configuration file path. If an environment
    variable for the config path is set, it uses that; otherwise, it defaults
    to the standard Qualibrate path.
    """
    return get_config_file(
        os.environ.get(CONFIG_PATH_ENV_NAME, QUALIBRATE_PATH),
        DEFAULT_ACTIVE_MACHINE_CONFIG_FILENAME,
        raise_not_exists=False,
    )


def get_config_dict(
    config_path: Path,
    config_key: Optional[str],
    config: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    if config is None or config_key is None or config_key not in config:
        config = read_config_file(config_path, solve_references=False)
    if config is None:
        raise RuntimeError("Couldn't read config file")
    return dict(config.get(cast(str, config_key), {}))


def get_config_dict_from_subpath(
    config_path: Path,
    subpath: Optional[str],
    config: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
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
    config_key: str,
    config_model_class: type[ConfigModel],
    config: Optional[dict[str, Any]] = None,
) -> ConfigModel:
    """Retrieve the configuration settings.

        Args:
        config_path: Path to the configuration file.
        config: Optional pre-loaded configuration data. If not provided, it
            will load and resolve references from the config file.

    Returns:
        An instance of QualibrateSettings with the loaded configuration.

    Raises:
        RuntimeError: If the configuration file cannot be read or if the
            configuration state is invalid.
    """
    model_config_dict = get_config_dict(config_path, config_key, config)
    settings = get_config_model_or_print_error(
        model_config_dict,
        config_model_class,
        config_key,
    )
    if settings is None:
        raise RuntimeError(
            f"Invalid config {config_model_class.__name__} state"
        )
    return settings


def get_qualibrate_settings(
    config_path: Path,
    config: Optional[dict[str, Any]] = None,
) -> QualibrateSettings:
    """Retrieve the Qualibrate configuration settings.

    Args:
        config_path: Path to the configuration file.
        config: Optional pre-loaded configuration data. If not provided, it
            will load and resolve references from the config file.

    Returns:
        An instance of QualibrateSettings with the loaded configuration.

    Raises:
        RuntimeError: If the configuration file cannot be read or if the
            configuration state is invalid.
    """
    return get_config_model(
        config_path,
        config_key=QUALIBRATE_CONFIG_KEY,
        config_model_class=QualibrateSettings,
        config=config,
    )


def get_active_machine_settings(
    config_path: Path,
    config: Optional[dict[str, Any]] = None,
) -> ActiveMachineSettings:
    """Retrieve the active machine configuration settings.

    Args:
        config_path: Path to the configuration file.
        config: Optional pre-loaded configuration data. If not provided, it
            will load and resolve references from the config file.

    Returns:
        An instance of ActiveMachineSettings with the loaded configuration.

    Raises:
        RuntimeError: If the configuration file cannot be read or if the
            configuration state is invalid.
    """
    return get_config_model(
        config_path,
        config_key=ACTIVE_MACHINE_CONFIG_KEY,
        config_model_class=ActiveMachineSettings,
        config=config,
    )
