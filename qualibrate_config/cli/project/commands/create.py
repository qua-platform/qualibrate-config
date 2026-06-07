import sys
from pathlib import Path

import click

from qualibrate_config.cli.vars import (
    CALIBRATION_LIBRARY_FOLDER_HELP,
    CONFIG_PATH_HELP,
    QUAM_STATE_PATH_HELP,
    STORAGE_LOCATION_HELP,
)
from qualibrate_config.core.project.create import (
    create_project,
)
from qualibrate_config.vars import (
    DEFAULT_CONFIG_FILEPATH,
)

__all__ = ["create_command"]


@click.command(name="create")
@click.argument("name", type=str)
@click.option(
    "--config-path",
    type=click.Path(exists=True, path_type=Path),
    default=DEFAULT_CONFIG_FILEPATH,
    show_default=True,
    help=CONFIG_PATH_HELP,
)
@click.option(
    "--storage-location",
    type=click.Path(
        file_okay=False, dir_okay=True, resolve_path=True, path_type=Path
    ),
    required=False,
    help=STORAGE_LOCATION_HELP,
)
@click.option(
    "--calibration-library-folder",
    type=click.Path(
        file_okay=False, dir_okay=True, resolve_path=True, path_type=Path
    ),
    required=False,
    help=CALIBRATION_LIBRARY_FOLDER_HELP,
)
@click.option(
    "--quam-state-path",
    type=click.Path(
        file_okay=False, dir_okay=True, resolve_path=True, path_type=Path
    ),
    required=False,
    help=QUAM_STATE_PATH_HELP,
)
@click.option(
    "--yes",
    "-y",
    "assume_yes",
    is_flag=True,
    default=False,
    help="Skip confirmation of expanded path values.",
)
@click.pass_context
def create_command(
    ctx: click.Context,
    name: str,
    config_path: Path,
    storage_location: Path | None,
    calibration_library_folder: Path | None,
    quam_state_path: Path | None,
    assume_yes: bool,
) -> None:
    supplied_paths = [
        ("--storage-location", storage_location),
        ("--calibration-library-folder", calibration_library_folder),
        ("--quam-state-path", quam_state_path),
    ]
    supplied_paths = [
        (flag, path) for flag, path in supplied_paths if path is not None
    ]
    if supplied_paths and not assume_yes:
        click.echo("The following paths will be saved to the project config:")
        for flag, path in supplied_paths:
            click.echo(f"  {flag}: {path}")
        if not click.confirm("Continue?", default=True):
            click.secho("Aborted.", fg="yellow")
            sys.exit(1)
    try:
        create_project(
            config_path,
            name,
            storage_location,
            calibration_library_folder,
            quam_state_path,
            ctx=ctx,
        )
    except ValueError as e:
        click.secho(str(e), fg="red")
        sys.exit(1)


if __name__ == "__main__":
    create_command(["test_creation"], standalone_mode=False)
