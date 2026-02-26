from pathlib import Path

from qualibrate_config.core.project.common import read_project_config_file
from qualibrate_config.core.project.create import (
    after_create_project,
    create_project_config_file,
    fill_project_calibration_library_folder,
    fill_project_database,
    fill_project_quam_state_path,
    fill_project_storage_location,
    rollback_project_creation,
)
from qualibrate_config.core.project.path import get_project_config_path
from qualibrate_config.models import DBConfig


def update_project(
    config_path: Path,
    name: str,
    storage_location: Path | None = None,
    calibration_library_folder: Path | None = None,
    quam_state_path: Path | None = None,
    database: DBConfig | None = None,
) -> None:
    qualibrate_path = config_path.parent
    project_config_path = get_project_config_path(qualibrate_path, name)

    if not project_config_path.exists():
        raise ValueError(f"Project '{name}' does not exist.")

    existing_config = read_project_config_file(config_path, name)

    fill_project_storage_location(existing_config, storage_location)
    fill_project_calibration_library_folder(
        existing_config, calibration_library_folder
    )
    fill_project_quam_state_path(existing_config, quam_state_path)
    fill_project_database(existing_config, database)
    try:
        create_project_config_file(qualibrate_path, name, existing_config)
        after_create_project(storage_location, quam_state_path)
    except Exception as exc:
        rollback_project_creation(
            qualibrate_path, name, storage_location, quam_state_path
        )
        raise ValueError(f"Project update failed. {exc}") from exc
