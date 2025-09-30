import inspect
import sys
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar, cast, overload

import tomli_w

from qualibrate_config.core.approve import print_and_confirm
from qualibrate_config.core.project.path import get_project_path
from qualibrate_config.file import get_config_file
from qualibrate_config.models import BaseConfig, QualibrateConfig
from qualibrate_config.qulibrate_types import RawConfigType
from qualibrate_config.vars import DEFAULT_CONFIG_FILENAME

if sys.version_info[:2] < (3, 11):
    import tomli as tomllib  # type: ignore[unused-ignore,import-not-found]
else:
    import tomllib


__all__ = [
    "ConfigType",
    "get_config_file_content",
    "simple_write",
    "qualibrate_after_write_cb",
    "write_config",
]

ConfigType = TypeVar("ConfigType", bound=BaseConfig)
# Non-generic callback alias to avoid "Missing type parameters" errors
Callback = (
    Callable[[BaseConfig], None] | Callable[[BaseConfig, Path | None], None]
)


def get_config_file_content(config_path: Path) -> tuple[RawConfigType, Path]:
    """Returns config and path to file"""
    config_file = get_config_file(
        config_path, DEFAULT_CONFIG_FILENAME, raise_not_exists=False
    )
    # TODO: first location of tomllib.loads
    if config_file.is_file():
        return tomllib.loads(config_file.read_text()), config_path
    return {}, config_file


def simple_write(path: Path, config: RawConfigType) -> None:
    with path.open("wb") as f_out:
        tomli_w.dump(config, f_out)


def qualibrate_after_write_cb(
    config: BaseConfig,
    config_file: Path | None = None,
) -> None:
    if config.project in config.storage.location.parts:
        config.storage.location.mkdir(parents=True, exist_ok=True)
    else:
        (config.storage.location / config.project).mkdir(
            parents=True, exist_ok=True
        )
    if config_file is not None:
        project_path = get_project_path(config_file.parent, config.project)
        project_path.mkdir(parents=True, exist_ok=True)
        (project_path / DEFAULT_CONFIG_FILENAME).touch()


# Overloads tell mypy the two legal shapes
@overload
def _call_cb(cb: None, config: BaseConfig, config_file: Path) -> None: ...
@overload
def _call_cb(
    cb: Callable[[BaseConfig], None], config: BaseConfig, config_file: Path
) -> None: ...
@overload
def _call_cb(
    cb: Callable[[BaseConfig, Path | None], None],
    config: BaseConfig,
    config_file: Path,
) -> None: ...
def _call_cb(
    cb: Callback | None,
    config: BaseConfig,
    config_file: Path,
) -> None:
    if cb is None:
        return
    # Runtime dispatch, then cast to keep mypy satisfied
    params_cnt = len(inspect.signature(cb).parameters)
    if params_cnt == 1:
        cb1 = cast(Callable[[BaseConfig], None], cb)
        cb1(config)
    else:
        cb2 = cast(Callable[[BaseConfig, Path | None], None], cb)
        cb2(config, config_file)


def write_config(
    config_file: Path,
    common_config: RawConfigType,
    config: ConfigType,
    config_key: str,
    before_write_cb: Callback | None = None,
    after_write_cb: Callback | None = None,
    confirm: bool = True,
    check_generator: bool = False,
) -> None:
    exported_data = config.serialize(exclude_none=True)
    common_config[config_key] = exported_data
    if confirm or check_generator:
        print_and_confirm(config_file, common_config, check_generator)

    _call_cb(before_write_cb, config, config_file)

    if not config_file.parent.exists():
        config_file.parent.mkdir(parents=True)
    simple_write(config_file, common_config)

    if after_write_cb is None and isinstance(config, QualibrateConfig):
        after_write_cb = qualibrate_after_write_cb
    _call_cb(after_write_cb, config, config_file)
