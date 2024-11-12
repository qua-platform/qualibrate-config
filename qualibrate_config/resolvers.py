import os
from pathlib import Path
from typing import Any, Optional

from qualibrate_config.file import get_config_file
from qualibrate_config.models import ActiveMachineSettings, QualibrateSettings
from qualibrate_config.validation import (
    get_config_model_or_print_error,
    get_config_solved_references_or_print_error,
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
    "get_qualibrate_config_path",
    "get_qualibrate_settings",
]


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
    if config is None:
        config = get_config_solved_references_or_print_error(config_path)
    if config is None:
        raise RuntimeError("Couldn't read config file")
    qs = get_config_model_or_print_error(
        config.get(QUALIBRATE_CONFIG_KEY, {}),
        QualibrateSettings,
        QUALIBRATE_CONFIG_KEY,
    )
    if qs is None:
        raise RuntimeError("Invalid config state")
    return qs


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
    if config is None:
        config = get_config_solved_references_or_print_error(config_path)
    if config is None:
        raise RuntimeError("Couldn't read config file")
    ams = get_config_model_or_print_error(
        config.get(ACTIVE_MACHINE_CONFIG_KEY, {}),
        ActiveMachineSettings,
        ACTIVE_MACHINE_CONFIG_KEY,
    )
    if ams is None:
        raise RuntimeError("Invalid config state")
    return ams
