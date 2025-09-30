import shutil
from collections.abc import Iterable, Mapping
from copy import deepcopy
from pathlib import Path
from typing import Any

import jsonpatch
import tomli_w
from click import Context

from qualibrate_config.core.content import get_config_file_content
from qualibrate_config.core.from_sources import qualibrate_config_from_sources
from qualibrate_config.core.project.p_list import list_projects
from qualibrate_config.core.project.path import (
    get_project_config_path,
    get_project_path,
)
from qualibrate_config.models import PathSerializer, QualibrateTopLevelConfig
from qualibrate_config.validation import validate_version_and_migrate_if_needed
from qualibrate_config.vars import (
    QUALIBRATE_CONFIG_KEY,
    QUAM_CONFIG_KEY,
    QUAM_STATE_PATH_CONFIG_KEY,
)


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


def _fill_path(
    config: dict[str, Any], path: Iterable[str], key: str, value: Path | None
) -> None:
    if value is None:
        return
    c_item = config
    for p in path:
        c_item = c_item.setdefault(p, {})
    c_item[key] = PathSerializer.serialize_path(value)


def fill_project_quam_state_path(
    common_config: dict[str, Any], quam_state_path: Path | None
) -> None:
    _fill_path(
        common_config,
        [QUAM_CONFIG_KEY],
        QUAM_STATE_PATH_CONFIG_KEY,
        quam_state_path,
    )


def fill_project_storage_location(
    common_config: dict[str, Any], storage_location: Path | None
) -> None:
    _fill_path(
        common_config,
        [QUALIBRATE_CONFIG_KEY, "storage"],
        "location",
        storage_location,
    )


def fill_project_calibration_library_folder(
    common_config: dict[str, Any], calibration_library_folder: Path | None
) -> None:
    _fill_path(
        common_config,
        [QUALIBRATE_CONFIG_KEY, "calibration_library"],
        "folder",
        calibration_library_folder,
    )


def after_create_project(
    storage_location: Path | None,
    quam_state_path: Path | None,
) -> None:
    if storage_location:
        storage_location.mkdir(parents=True, exist_ok=True)
    if quam_state_path:
        quam_state_path.mkdir(parents=True, exist_ok=True)


def create_project_config_file(
    qualibrate_path: Path,
    project_name: str,
    config_overrides: Mapping[str, Any] | None = None,
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
    storage_path: Path | None,
    quam_state_path: Path | None,
) -> None:
    project_path = get_project_path(qualibrate_path, project_name)
    for p in (project_path, storage_path, quam_state_path):
        if p and p.is_dir():
            shutil.rmtree(p)


def config_for_project_from_context(
    common_config: dict[str, Any],
    storage_location: Path | None,
    calibration_library_folder: Path | None,
    quam_state_path: Path | None,
    context: Context | None,
) -> dict[str, Any]:
    if context is None:
        raise ValueError("Context isn't passed.")
    q_config = common_config.get(QUALIBRATE_CONFIG_KEY, {})
    required_subconfigs = ("storage",)
    optional_subconfigs = (
        ("calibration_library",)
        if (
            calibration_library_folder
            or q_config.get("calibration_library") is not None
        )
        else tuple()
    )
    q_config = qualibrate_config_from_sources(
        context,
        q_config,
        required_subconfigs,
        optional_subconfigs,
    )
    if (
        calibration_library_folder is not None
        and q_config.get("calibration_library", {}).get("resolver") is None
    ):
        raise ValueError(
            "Calibration library folder can't be specified without a resolver."
        )
    qs = QualibrateTopLevelConfig({QUALIBRATE_CONFIG_KEY: q_config})
    common_config.update(qs.serialize())
    fill_project_quam_state_path(common_config, quam_state_path)
    return common_config


def config_for_project_from_args(
    common_config: dict[str, Any],
    storage_location: Path | None,
    calibration_library_folder: Path | None,
    quam_state_path: Path | None,
    context: Context | None,
) -> dict[str, Any]:
    if context is not None:
        raise ValueError("Context is passed.")
    fill_project_storage_location(common_config, storage_location)
    fill_project_calibration_library_folder(
        common_config, calibration_library_folder
    )
    fill_project_quam_state_path(common_config, quam_state_path)
    return common_config


def create_project(
    config_path: Path,
    name: str,
    storage_location: Path | None,
    calibration_library_folder: Path | None,
    quam_state_path: Path | None,
    ctx: Context | None = None,
) -> None:
    qualibrate_path = config_path.parent
    try:
        projects = list_projects(qualibrate_path)
    except NotADirectoryError:
        pass
    else:
        if name in projects:
            raise ValueError(f"Project '{name}' already exists.")
    common_config, config_file = get_config_file_content(config_path)
    common_config, config_file = validate_version_and_migrate_if_needed(
        common_config, config_file
    )
    old_config = deepcopy(common_config)
    config_for_project = (
        config_for_project_from_context if ctx else config_for_project_from_args
    )
    common_config = config_for_project(
        common_config,
        storage_location,
        calibration_library_folder,
        quam_state_path,
        ctx,
    )
    patches = jsonpatch.make_patch(old_config, common_config)
    project_config = jsonpatch_to_dict(patches)
    try:
        create_project_config_file(qualibrate_path, name, project_config)
        after_create_project(storage_location, quam_state_path)
    except Exception as exc:
        rollback_project_creation(
            qualibrate_path, name, storage_location, quam_state_path
        )
        raise ValueError(f"Project creation failed. {exc}") from exc
