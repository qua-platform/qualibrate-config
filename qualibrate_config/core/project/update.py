import logging
from copy import deepcopy
from pathlib import Path

import jsonpatch
import tomli_w

from qualibrate_config.core.content import get_config_file_content
from qualibrate_config.core.project.create import (
    after_create_project,
    config_for_project_from_args,
    jsonpatch_to_dict,
)
from qualibrate_config.core.project.path import get_project_config_path
from qualibrate_config.models import DatabaseStateConfig, DBConfig
from qualibrate_config.validation import validate_version_and_migrate_if_needed

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

    # Load and validate base config
    base_config, config_file = get_config_file_content(config_path)
    base_config, config_file = validate_version_and_migrate_if_needed(
        base_config, config_file
    )
    old_base_config = deepcopy(base_config)

    # Apply updates using the same helper as create_project
    base_config = config_for_project_from_args(
        base_config,
        storage_location,
        calibration_library_folder,
        quam_state_path,
        database,
        database_state,
        None,  # context
    )

    # Compute diff: only write values that differ from original base
    patches = jsonpatch.make_patch(old_base_config, base_config)
    project_config = jsonpatch_to_dict(patches)

    # Use atomic write: write to temp file first, then replace original
    temp_config_path = project_config_path.with_suffix(".tmp")
    try:
        # Ensure parent directory exists
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write only the diff to temporary file
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
