import logging
from pathlib import Path

import tomli_w

from qualibrate_config.core.project.common import read_project_config_file
from qualibrate_config.core.project.create import (
    after_create_project,
    config_for_project_from_args,
)
from qualibrate_config.core.project.path import get_project_config_path
from qualibrate_config.models import DatabaseStateConfig, DBConfig

logger = logging.getLogger(__name__)


def update_project(
    config_path: Path,
    name: str,
    storage_location: Path | None = None,
    calibration_library_folder: Path | None = None,
    quam_state_path: Path | None = None,
    database: DBConfig | None = None,
    database_state: DatabaseStateConfig | None = None,
) -> None:
    qualibrate_path = config_path.parent
    project_config_path = get_project_config_path(qualibrate_path, name)

    if not project_config_path.exists():
        raise ValueError(f"Project '{name}' does not exist.")

    # Apply onto the project's own file: copying the global config in would
    # freeze its values into the project and drop the project's overrides.
    project_config = config_for_project_from_args(
        read_project_config_file(config_path, name),
        storage_location,
        calibration_library_folder,
        quam_state_path,
        database,
        database_state,
        None,  # context
    )

    # Use atomic write: write to temp file first, then replace original
    temp_config_path = project_config_path.with_suffix(".tmp")
    try:
        # Ensure parent directory exists
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the full project config to temporary file
        with temp_config_path.open("wb") as f_out:
            tomli_w.dump(project_config, f_out)

        # Create directories if needed
        after_create_project(storage_location, quam_state_path)

        # Only if everything succeeds, atomically replace the original file
        temp_config_path.replace(project_config_path)
        logger.info(f"Successfully updated project '{name}'")

    except Exception as exc:
        # Log the full exception details
        logger.error(
            f"Project update failed for '{name}': {type(exc).__name__}: {exc}",
            exc_info=True,
        )

        # Clean up temp file if it exists
        if temp_config_path.exists():
            try:
                temp_config_path.unlink()
                logger.debug(
                    f"Cleaned up temporary config file for project '{name}'"
                )
            except Exception as cleanup_exc:
                logger.warning(f"Failed to clean up temp file: {cleanup_exc}")

        raise ValueError(
            f"Project update failed. {type(exc).__name__}: {exc}"
        ) from exc
