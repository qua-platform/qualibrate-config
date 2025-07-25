from pathlib import Path

import click

from qualibrate_config.cli.vars import CONFIG_PATH_HELP
from qualibrate_config.core.content import get_config_file_content
from qualibrate_config.core.project.common import get_project_from_common_config
from qualibrate_config.vars import DEFAULT_CONFIG_FILEPATH

__all__ = ["current_command"]


@click.command(name="current")
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
def current_command(
    config_path: Path,
) -> None:
    common_config, config_file = get_config_file_content(config_path)
    project = get_project_from_common_config(common_config)
    if project is None:
        click.secho(
            "Can't resolve current config version from file. Please regenerate "
            "config using `qualibrate-config config` command.",
            fg="yellow",
        )
        return
    click.echo(f"Current project is {project}")


if __name__ == "__main__":
    current_command([], standalone_mode=False)
