import sys
from pathlib import Path

import tomli_w

from qualibrate_config.cli.utils.approve import print_and_confirm
from qualibrate_config.file import get_config_file
from qualibrate_config.models import QualibrateConfig
from qualibrate_config.qulibrate_types import RawConfigType
from qualibrate_config.vars import (
    DEFAULT_CONFIG_FILENAME,
    QUALIBRATE_CONFIG_KEY,
)

if sys.version_info[:2] < (3, 11):
    import tomli as tomllib
else:
    import tomllib


def get_config(config_path: Path) -> tuple[RawConfigType, Path]:
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


def write_config(
    config_file: Path,
    common_config: RawConfigType,
    qs: QualibrateConfig,
    confirm: bool = True,
    check_generator: bool = False,
) -> None:
    exported_data = qs.serialize(exclude_none=True)
    common_config[QUALIBRATE_CONFIG_KEY] = exported_data
    if confirm or check_generator:
        print_and_confirm(config_file, common_config, check_generator)
    if qs.project in qs.storage.location.parts:
        qs.storage.location.mkdir(parents=True, exist_ok=True)
    else:
        (qs.storage.location / qs.project).mkdir(parents=True, exist_ok=True)
    if not config_file.parent.exists():
        config_file.parent.mkdir(parents=True)
    simple_write(config_file, common_config)
