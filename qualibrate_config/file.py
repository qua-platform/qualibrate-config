import sys
from pathlib import Path

from qualibrate_config.core.project.common import (
    get_project_from_common_config,
    read_project_config_file,
)
from qualibrate_config.core.utils import recursive_update_dict
from qualibrate_config.qulibrate_types import RawConfigType
from qualibrate_config.references.resolvers import resolve_references
from qualibrate_config.vars import (
    DEFAULT_CONFIG_FILENAME,
    QUALIBRATE_CONFIG_KEY,
    QUALIBRATE_PATH,
)

if sys.version_info[:2] < (3, 11):
    import tomli as tomllib  # type: ignore[unused-ignore,import-not-found]
else:
    import tomllib


def _get_config_file_from_dir(
    dir_path: Path,
    default_config_specific_filename: str | Path,
    raise_not_exists: bool = True,
) -> Path:
    default_qualibrate = dir_path / default_config_specific_filename
    if default_qualibrate.is_file():
        return default_qualibrate
    default_common = dir_path / DEFAULT_CONFIG_FILENAME
    if default_common.is_file():
        return default_common
    if raise_not_exists:
        raise FileNotFoundError(f"Config file in dir {dir_path} does not exist")
    return default_common


def get_config_file(
    config_path: str | Path | None,
    default_config_specific_filename: str | Path,
    raise_not_exists: bool = True,
) -> Path:
    if config_path is None:
        return _get_config_file_from_dir(
            QUALIBRATE_PATH, default_config_specific_filename, raise_not_exists
        )
    config_path_ = Path(config_path)
    if config_path_.is_file():
        return config_path_
    if config_path_.is_dir():
        return _get_config_file_from_dir(
            config_path_, default_config_specific_filename
        )
    if raise_not_exists:
        raise OSError("Unexpected config file path")
    return config_path_


def read_config_file(
    config_file: Path,
    solve_references: bool = True,
    override_project: str | None = None,
) -> RawConfigType:
    # TODO: second location of tomllib.loads
    with config_file.open("rb") as fin:
        config: RawConfigType = tomllib.load(fin)  # typing for mypy tomli
    if project := (override_project or get_project_from_common_config(config)):
        project_config = read_project_config_file(config_file, project)
        project_config.setdefault(QUALIBRATE_CONFIG_KEY, {})["project"] = (
            project
        )
        config = recursive_update_dict(config, project_config)
    if not solve_references:
        return config
    return resolve_references(config)
