import sys
from pathlib import Path
from typing import Optional, cast

from qualibrate_config.core.project.path import get_project_config_path
from qualibrate_config.qulibrate_types import RawConfigType
from qualibrate_config.vars import (
    QUALIBRATE_CONFIG_KEY,
)

if sys.version_info[:2] < (3, 11):
    import tomli as tomllib  # type: ignore[unused-ignore,import-not-found]
else:
    import tomllib


def get_project_from_common_config(config: RawConfigType) -> Optional[str]:
    return cast(
        Optional[str], config.get(QUALIBRATE_CONFIG_KEY, {}).get("project")
    )


def read_project_config_file(
    config_path: Path,
    project_name: str,
) -> Optional[RawConfigType]:
    project_config = get_project_config_path(config_path.parent, project_name)
    if not project_config.is_file():
        return None
    with project_config.open("rb") as fin:
        return cast(RawConfigType, tomllib.load(fin))  # typing for mypy tomli
