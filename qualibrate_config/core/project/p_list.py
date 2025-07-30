import datetime
from pathlib import Path

import click

from qualibrate_config.core.project.path import (
    get_project_path,
    get_projects_path,
)


def list_projects(qualibrate_path: Path) -> list[str]:
    return list(
        map(
            lambda p: p.name,
            filter(Path.is_dir, get_projects_path(qualibrate_path).iterdir()),
        )
    )


def print_simple_projects_list(qualibrate_path: Path) -> None:
    click.echo("\n".join(list_projects(qualibrate_path)))


def print_verbose_projects_list(qualibrate_path: Path) -> None:
    for p_name in list_projects(qualibrate_path):
        project_path = get_project_path(qualibrate_path, p_name)
        project_stat = project_path.stat()
        created = datetime.datetime.fromtimestamp(round(project_stat.st_ctime))
        click.echo(f"Project {p_name}. Created: {created}.")
