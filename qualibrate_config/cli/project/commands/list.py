from pathlib import Path

import click

from qualibrate_config.cli.vars import CONFIG_PATH_HELP
from qualibrate_config.core.project.p_list import (
    print_simple_projects_list,
    print_verbose_projects_list,
)
from qualibrate_config.vars import DEFAULT_CONFIG_FILEPATH

__all__ = ["list_command"]


@click.command(name="list")
@click.option(
    "--config-path",
    type=click.Path(exists=True, path_type=Path),
    default=DEFAULT_CONFIG_FILEPATH,
    show_default=True,
    help=CONFIG_PATH_HELP,
)
@click.option("--verbose", "-v", is_flag=True)
def list_command(config_path: Path, verbose: bool) -> None:
    print_ = (
        print_verbose_projects_list if verbose else print_simple_projects_list
    )
    print_(config_path)


if __name__ == "__main__":
    list_command([], standalone_mode=False)
