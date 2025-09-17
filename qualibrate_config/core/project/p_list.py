import datetime
import sys
from os import stat_result
from pathlib import Path

import click

from qualibrate_config.core.project.common import read_project_config_file
from qualibrate_config.core.project.model import Project
from qualibrate_config.core.project.path import (
    get_project_path,
    get_projects_path,
)
from qualibrate_config.file import read_config_file
from qualibrate_config.vars import QUALIBRATE_CONFIG_KEY


def _dt_from_ts(ts: float) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(round(ts))


def _stat_ctime(storage_stat: stat_result) -> float:
    if sys.version_info >= (3, 12) and sys.platform == "win32":
        return storage_stat.st_birthtime
    return storage_stat.st_ctime


def _file_stat_ctime(p: Path) -> float:
    return _stat_ctime(p.stat())


def _file_stat_mtime(p: Path) -> float:
    return p.stat().st_mtime


def _created_at_from_storage(
    storage_path: Path, storage_stat: stat_result
) -> datetime.datetime:
    first_create_p = min(
        (p for p in storage_path.glob("*/#*") if p.is_dir()),
        key=_file_stat_ctime,
        default=None,
    )
    if first_create_p is None:
        return _dt_from_ts(_stat_ctime(storage_stat))
    return _dt_from_ts(
        min(_stat_ctime(storage_stat), _file_stat_ctime(first_create_p))
    )


def _last_modified_at_from_storage(
    storage_path: Path, storage_stat: stat_result
) -> datetime.datetime:
    first_create_p = max(
        (p for p in storage_path.glob("*/#*") if p.is_dir()),
        key=_file_stat_mtime,
        default=None,
    )
    if first_create_p is None:
        return _dt_from_ts(storage_stat.st_mtime)
    return _dt_from_ts(
        max(storage_stat.st_mtime, _file_stat_mtime(first_create_p))
    )


def _storage_stat(
    storage_path: Path,
) -> tuple[int, datetime.datetime, datetime.datetime]:
    nodes_number = sum(
        (1 for p in storage_path.glob("*/#*") if p.is_dir()),
        start=0,
    )
    storage_stat = storage_path.stat()
    created_at = _created_at_from_storage(storage_path, storage_stat)
    last_modified_at = _last_modified_at_from_storage(
        storage_path, storage_stat
    )
    return nodes_number, created_at, last_modified_at


def _project_stat_dir(
    project_path: Path,
) -> tuple[int, datetime.datetime, datetime.datetime]:
    stat = project_path.stat()
    return 0, _dt_from_ts(stat.st_ctime), _dt_from_ts(stat.st_mtime)


def project_stat(
    qualibrate_path: Path, project: str, config_path: Path
) -> Project:
    project_path = get_project_path(qualibrate_path, project)

    config_dict = read_config_file(config_path, override_project=project)
    project_config = read_project_config_file(config_path, project)
    storage_location = (
        config_dict.get(QUALIBRATE_CONFIG_KEY, {})
        .get("storage", {})
        .get("location")
    )
    if storage_location:
        storage_path = Path(storage_location)
        if storage_path.is_dir():
            nodes_number, created_at, last_modified_at = _storage_stat(
                storage_path
            )
        else:
            nodes_number, created_at, last_modified_at = _project_stat_dir(
                project_path
            )
    else:
        nodes_number, created_at, last_modified_at = _project_stat_dir(
            project_path
        )
    return Project(
        name=project,
        nodes_number=nodes_number,
        created_at=created_at.astimezone(),
        last_modified_at=last_modified_at.astimezone(),
        updates=project_config,
    )


def list_projects(qualibrate_path: Path) -> list[str]:
    projects_path = get_projects_path(qualibrate_path)
    if not projects_path.is_dir():
        raise NotADirectoryError(
            f"Projects path '{projects_path}' is not a directory"
        )
    return list(
        map(
            lambda p: p.name,
            filter(Path.is_dir, projects_path.iterdir()),
        )
    )


def verbose_list_projects(
    config_path: Path,
) -> dict[str, Project]:
    qualibrate_path = config_path.parent
    return {
        p_name: project_stat(qualibrate_path, p_name, config_path)
        for p_name in list_projects(qualibrate_path)
    }


def print_simple_projects_list(
    config_path: Path,
) -> None:
    click.echo("\n".join(list_projects(config_path.parent)))


def print_verbose_projects_list(
    config_path: Path,
) -> None:
    for p_stat in verbose_list_projects(config_path).values():
        click.echo(p_stat.verbose_str())
