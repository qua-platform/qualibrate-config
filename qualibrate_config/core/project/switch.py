from pathlib import Path

import click

from qualibrate_config.core.content import get_config_file_content, simple_write
from qualibrate_config.core.project.path import get_project_path
from qualibrate_config.vars import QUALIBRATE_CONFIG_KEY


def switch_project(
    config_path: Path, project: str, *, raise_if_error: bool = False
) -> bool:
    project_path = get_project_path(config_path.parent, project)
    if not project_path.exists():
        error_msg = (
            f"Can't switch project to '{project}'. "
            f"There is no specified project in {project_path.parent}."
        )
        if raise_if_error:
            raise ValueError(error_msg)
        click.secho(error_msg, fg="red")
        return False
    common_config, config_file = get_config_file_content(config_path)
    common_config[QUALIBRATE_CONFIG_KEY]["project"] = project
    simple_write(config_file, common_config)
    return True
