from copy import deepcopy
from pathlib import Path
from typing import Optional

import click
import jsonpatch

from qualibrate_config.cli.vars import (
    CALIBRATION_LIBRARY_FOLDER_HELP,
    CONFIG_PATH_HELP,
    QUAM_STATE_PATH_HELP,
    STORAGE_LOCATION_HELP,
)
from qualibrate_config.core.content import get_config_file_content
from qualibrate_config.core.from_sources import qualibrate_config_from_sources
from qualibrate_config.core.project.create import (
    after_create_project,
    create_project,
    fill_project_quam_state_path,
    jsonpatch_to_dict,
    rollback_project_creation,
)
from qualibrate_config.core.project.p_list import list_projects
from qualibrate_config.models import QualibrateTopLevelConfig
from qualibrate_config.validation import validate_version_and_migrate_if_needed
from qualibrate_config.vars import (
    DEFAULT_CONFIG_FILEPATH,
    QUALIBRATE_CONFIG_KEY,
)

__all__ = ["create_command"]


@click.command(name="create")
@click.argument("name", type=str)
@click.option(
    "--config-path",
    type=click.Path(
        exists=False,
        path_type=Path,
    ),
    default=DEFAULT_CONFIG_FILEPATH,
    show_default=True,
    help=CONFIG_PATH_HELP,
)
@click.option(
    "--storage-location",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    help=STORAGE_LOCATION_HELP,
)
@click.option(
    "--calibration-library-folder",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    help=CALIBRATION_LIBRARY_FOLDER_HELP,
)
@click.option(
    "--quam-state-path",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    help=QUAM_STATE_PATH_HELP,
)
@click.pass_context
def create_command(
    ctx: click.Context,
    name: str,
    config_path: Path,
    storage_location: Optional[Path],
    calibration_library_folder: Optional[Path],
    quam_state_path: Optional[Path],
) -> None:
    if not config_path.is_file():
        click.secho("Config file isn't defined.", fg="red")
        return
    qualibrate_path = config_path.parent
    projects = list_projects(qualibrate_path)
    if name in projects:
        click.secho(f"Project '{name}' already exists.", fg="red")
        return
    common_config, config_file = get_config_file_content(config_path)
    common_config, config_file = validate_version_and_migrate_if_needed(
        common_config, config_file
    )
    old_config = deepcopy(common_config)
    qualibrate_config = common_config.get(QUALIBRATE_CONFIG_KEY, {})
    required_subconfigs = ("storage",)
    optional_subconfigs = ("calibration_library",)
    qualibrate_config = qualibrate_config_from_sources(
        ctx,
        qualibrate_config,
        required_subconfigs,
        optional_subconfigs,
    )
    qs = QualibrateTopLevelConfig({QUALIBRATE_CONFIG_KEY: qualibrate_config})
    common_config.update(qs.serialize())
    fill_project_quam_state_path(common_config, quam_state_path)

    patches = jsonpatch.make_patch(old_config, common_config)
    project_config = jsonpatch_to_dict(patches)
    try:
        create_project(config_path.parent, name, project_config)
        after_create_project(storage_location, quam_state_path)
    except Exception as exc:
        click.secho(f"Project creation failed. {exc}", fg="red")
        rollback_project_creation(
            qualibrate_path, name, storage_location, quam_state_path
        )


if __name__ == "__main__":
    create_command(["test_creation"], standalone_mode=False)
