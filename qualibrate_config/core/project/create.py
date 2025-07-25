import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Optional

from qualibrate_config.core.project.path import get_project_config_path

if sys.version_info[:2] < (3, 11):
    import tomli as tomllib  # type: ignore[unused-ignore,import-not-found]
else:
    import tomllib


def create_project(
    qualibrate_path: Path,
    project_name: str,
    config_overrides: Optional[Mapping[str, Any]] = None,
) -> None:
    config_filepath = get_project_config_path(qualibrate_path, project_name)
    config_filepath.parent.mkdir(parents=True)
    if config_overrides:
        with config_filepath.open("wb") as f_out:
            tomllib.dump(config_overrides, f_out)
    else:
        config_filepath.touch()
