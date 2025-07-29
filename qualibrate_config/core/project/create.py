import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Optional

import jsonpatch
import tomli_w

from qualibrate_config.core.project.path import (
    get_project_config_path,
    get_project_path,
)
from qualibrate_config.models import PathSerializer
from qualibrate_config.vars import QUAM_CONFIG_KEY, QUAM_STATE_PATH_CONFIG_KEY


def jsonpatch_to_dict(patch: jsonpatch.JsonPatch) -> dict[str, Any]:
    d: dict[str, Any] = dict()
    replace_ops = filter(
        lambda op: isinstance(op, jsonpatch.ReplaceOperation), patch._ops
    )
    for op in replace_ops:
        path_ = d
        for part in op.pointer.parts[:-1]:
            if part not in path_:
                path_[part] = {}
            path_ = path_[part]
        path_[op.key] = op.operation["value"]
    return d


def fill_project_quam_state_path(
    common_config: dict[str, Any], quam_state_path: Optional[Path]
) -> None:
    if quam_state_path is None:
        return
    quam_config = common_config.setdefault(QUAM_CONFIG_KEY, {})
    quam_config[QUAM_STATE_PATH_CONFIG_KEY] = PathSerializer.serialize_path(
        quam_state_path
    )


def after_create_project(
    storage_location: Optional[Path],
    quam_state_path: Optional[Path],
) -> None:
    if storage_location:
        storage_location.mkdir(parents=True, exist_ok=True)
    if quam_state_path:
        quam_state_path.mkdir(parents=True, exist_ok=True)


def create_project(
    qualibrate_path: Path,
    project_name: str,
    config_overrides: Optional[Mapping[str, Any]] = None,
) -> None:
    config_filepath = get_project_config_path(qualibrate_path, project_name)
    config_filepath.parent.mkdir(parents=True, exist_ok=True)
    if config_overrides:
        with config_filepath.open("wb") as f_out:
            tomli_w.dump(config_overrides, f_out)
    else:
        config_filepath.touch()


def rollback_project_creation(
    qualibrate_path: Path,
    project_name: str,
    storage_path: Optional[Path],
    quam_state_path: Optional[Path],
) -> None:
    project_path = get_project_path(qualibrate_path, project_name)
    for p in (project_path, storage_path, quam_state_path):
        if p and p.is_dir():
            shutil.rmtree(p)
