import sys
from pathlib import Path

import click

__all__ = ["delete_command"]

from qualibrate_config.cli.vars import CONFIG_PATH_HELP
from qualibrate_config.core.project.delete import delete_project
from qualibrate_config.vars import DEFAULT_CONFIG_FILEPATH


@click.command(name="delete")
@click.argument("name", type=str)
@click.option(
    "--config-path",
    type=click.Path(exists=True, path_type=Path),
    default=DEFAULT_CONFIG_FILEPATH,
    show_default=True,
    help=CONFIG_PATH_HELP,
)
def delete_command(
    name: str,
    config_path: Path,
) -> None:
    try:
        delete_project(config_path, name)
    except RuntimeError as e:
        click.secho(f"Failed to remove project '{name}'. {e}", fg="red")
        sys.exit(1)
    else:
        click.echo(f"Successfully removed project '{name}'")


if __name__ == "__main__":
    delete_command([], standalone_mode=False)
