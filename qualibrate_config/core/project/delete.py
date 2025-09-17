import shutil
from pathlib import Path

from qualibrate_config.core.content import get_config_file_content
from qualibrate_config.core.project.common import get_project_from_common_config
from qualibrate_config.core.project.p_list import list_projects
from qualibrate_config.core.project.path import get_project_path


def delete_project(config_path: Path, project: str) -> None:
    qualibrate_path = config_path.parent
    try:
        projects = list_projects(qualibrate_path)
    except NotADirectoryError as e:
        # there is no any project
        raise RuntimeError("Projects dir doesn't exist.") from e
    if project not in projects:
        raise RuntimeError(f"Project '{project}' does not exist")
    common_config, config_file = get_config_file_content(config_path)
    current_project = get_project_from_common_config(common_config)
    if current_project and current_project == project:
        raise RuntimeError("Can't delete current project.")
    project_path = get_project_path(qualibrate_path, project)
    if project_path is None:
        raise RuntimeError(f"Can't resolve project '{project}' directory")
    shutil.rmtree(project_path)
