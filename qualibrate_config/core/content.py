import sys
from pathlib import Path
from typing import Callable, Optional, TypeVar

import tomli_w

from qualibrate_config.core.approve import print_and_confirm
from qualibrate_config.file import get_config_file
from qualibrate_config.models import BaseConfig
from qualibrate_config.qulibrate_types import RawConfigType
from qualibrate_config.vars import (
    DEFAULT_CONFIG_FILENAME,
)

if sys.version_info[:2] < (3, 11):
    import tomli as tomllib  # type: ignore[unused-ignore,import-not-found]
else:
    import tomllib


__all__ = [
    "ConfigType",
    "get_config_file_content",
    "simple_write",
    "qualibrate_before_write_cb",
    "write_config",
]

ConfigType = TypeVar("ConfigType", bound=BaseConfig)


def get_config_file_content(config_path: Path) -> tuple[RawConfigType, Path]:
    """Returns config and path to file"""
    config_file = get_config_file(
        config_path, DEFAULT_CONFIG_FILENAME, raise_not_exists=False
    )
    if config_file.is_file():
        return tomllib.loads(config_file.read_text()), config_path
    return {}, config_file


def simple_write(path: Path, config: RawConfigType) -> None:
    with path.open("wb") as f_out:
        tomli_w.dump(config, f_out)


def qualibrate_before_write_cb(config: ConfigType) -> None:
    if config.project in config.storage.location.parts:
        config.storage.location.mkdir(parents=True, exist_ok=True)
    else:
        (config.storage.location / config.project).mkdir(
            parents=True, exist_ok=True
        )


def write_config(
    config_file: Path,
    common_config: RawConfigType,
    config: ConfigType,
    config_key: str,
    before_write_cb: Optional[Callable[[ConfigType], None]] = None,
    confirm: bool = True,
    check_generator: bool = False,
) -> None:
    exported_data = config.serialize(exclude_none=True)
    common_config[config_key] = exported_data
    if confirm or check_generator:
        print_and_confirm(config_file, common_config, check_generator)
    if before_write_cb is None:
        before_write_cb = qualibrate_before_write_cb
    before_write_cb(config)
    if not config_file.parent.exists():
        config_file.parent.mkdir(parents=True)
    simple_write(config_file, common_config)
