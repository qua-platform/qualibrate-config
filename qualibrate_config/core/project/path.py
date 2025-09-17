from pathlib import Path

from qualibrate_config.vars import DEFAULT_CONFIG_FILENAME


def get_projects_path(qualibrate_path: Path) -> Path:
    return qualibrate_path / "projects"


def get_project_path(qualibrate_path: Path, project_name: str) -> Path:
    return get_projects_path(qualibrate_path) / project_name


def get_project_config_path(
    qualibrate_path: Path,
    project_name: str,
    config_filename: str = DEFAULT_CONFIG_FILENAME,
) -> Path:
    return get_project_path(qualibrate_path, project_name).joinpath(
        config_filename
    )
