from pathlib import Path

from qualibrate_config.core.content import get_config_file_content
from qualibrate_config.core.project.common import get_project_from_common_config
from qualibrate_config.core.project.path import get_project_config_path


def get_active_project(config_path: Path) -> str | None:
    common_config, config_file = get_config_file_content(config_path)
    project_name = get_project_from_common_config(common_config)
    if project_name is None:
        return None
    project_config = get_project_config_path(config_path.parent, project_name)
    if not project_config.is_file():
        return None
    return project_name
