import sys
from pathlib import Path

import click

from qualibrate_config.cli.vars import CONFIG_PATH_HELP
from qualibrate_config.core.project.active import get_active_project
from qualibrate_config.vars import DEFAULT_CONFIG_FILEPATH

__all__ = ["current_command"]


@click.command(name="current")
@click.option(
    "--config-path",
    type=click.Path(exists=True, path_type=Path),
    default=DEFAULT_CONFIG_FILEPATH,
    show_default=True,
    help=CONFIG_PATH_HELP,
)
def current_command(
    config_path: Path,
) -> None:
    project = get_active_project(config_path)
    if project is None:
        click.secho(
            "Can't resolve currently active project. If you have no "
            "project please create it. Otherwise please regenerate config "
            "using `qualibrate-config config` command.",
            fg="yellow",
        )
        sys.exit(1)
    click.echo(f"Current project is {project}")


if __name__ == "__main__":
    current_command([], standalone_mode=False)
