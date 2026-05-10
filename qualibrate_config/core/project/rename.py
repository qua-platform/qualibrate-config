import logging
from pathlib import Path

from qualibrate_config.core.project.path import (
    get_project_path,
)

logger = logging.getLogger(__name__)


def rename_project(
    config_path: Path,
    old_name: str,
    new_name: str,
) -> None:
    qualibrate_path = config_path.parent

    project_path = get_project_path(qualibrate_path, old_name)
    if not project_path.exists():
        raise ValueError(f"Project '{old_name}' does not exist.")

    new_project_path = get_project_path(qualibrate_path, new_name)
    if new_project_path.exists():
        raise ValueError(f"Project '{new_name}' already exists.")

    try:
        # Only if everything succeeds, atomically replace the original file
        project_path.rename(new_project_path)
        logger.info(
            f"Successfully renamed project '{old_name}' to '{new_name}'"
        )

    except Exception as exc:
        # Log the full exception details
        logger.error(
            f"Project rename failed from '{old_name}' to '{new_name}'",
            exc_info=True,
        )

        raise ValueError(
            f"Project rename failed from '{old_name}' to '{new_name}'"
        ) from exc
