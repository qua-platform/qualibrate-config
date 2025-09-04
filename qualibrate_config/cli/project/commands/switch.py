import sys
from pathlib import Path

import click

from qualibrate_config.cli.vars import CONFIG_PATH_HELP
from qualibrate_config.core.project.switch import switch_project
from qualibrate_config.vars import DEFAULT_CONFIG_FILEPATH

__all__ = ["switch_command"]


@click.command(name="switch")
@click.argument("project", type=str)
@click.option(
    "--config-path",
    type=click.Path(exists=True, path_type=Path),
    default=DEFAULT_CONFIG_FILEPATH,
    show_default=True,
    help=CONFIG_PATH_HELP,
)
def switch_command(project: str, config_path: Path) -> None:
    if switch_project(config_path, project):
        click.echo(f"Project switched to '{project}'.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    switch_command([], standalone_mode=False)
