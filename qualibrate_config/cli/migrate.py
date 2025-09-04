from pathlib import Path

import click

from qualibrate_config.cli.vars import CONFIG_PATH_HELP
from qualibrate_config.core.migration.migrate import run_migrations
from qualibrate_config.models import QualibrateConfig
from qualibrate_config.vars import DEFAULT_CONFIG_FILEPATH

__all__ = ["migrate_command"]


@click.command(name="migrate", help="Migrate qualibrate config files")
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
@click.argument("to_version", type=int, default=QualibrateConfig.version)
def migrate_command(config_path: Path, to_version: int) -> None:
    run_migrations(
        config_path=config_path,
        to_version=to_version,
    )


if __name__ == "__main__":
    migrate_command([], standalone_mode=False)
