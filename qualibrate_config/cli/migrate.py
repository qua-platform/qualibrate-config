from pathlib import Path

import click
import tomli_w

from qualibrate_config.cli.utils.content import get_config
from qualibrate_config.cli.utils.migration_utils import make_migrations
from qualibrate_config.models import QualibrateConfig
from qualibrate_config.models.qualibrate import QualibrateTopLevelConfig
from qualibrate_config.vars import (
    DEFAULT_CONFIG_FILENAME,
    QUALIBRATE_CONFIG_KEY,
    QUALIBRATE_PATH,
)

__all__ = ["migrate_command"]


@click.command(name="migrate")
@click.option(
    "--config-path",
    type=click.Path(
        exists=False,
        path_type=Path,
    ),
    default=QUALIBRATE_PATH / DEFAULT_CONFIG_FILENAME,
    show_default=True,
    help=(
        "Path to the configuration file. If the path points to a file, it will "
        "be read and the old configuration will be reused, except for the "
        "variables specified by the user. If the file does not exist, a new one"
        " will be created. If the path points to a directory, a check will be "
        "made to see if files with the default name exist."
    ),
)
@click.argument("to_version", type=int, default=QualibrateConfig.version)
@click.pass_context
def migrate_command(
    ctx: click.Context, config_path: Path, to_version: int
) -> None:
    common_config, config_file = get_config(config_path)
    if common_config == {}:
        click.secho("Config file wasn't found. Nothing to migrate", fg="yellow")
        return
    qualibrate_config = common_config.get(QUALIBRATE_CONFIG_KEY, {})
    from_version = qualibrate_config.get("version") or qualibrate_config.get(
        "config_version"
    )
    if from_version is None:
        click.secho(
            "Can't resolve current config version from file. Please regenerate "
            "config using `qualibrate-config config` command.",
            fg="yellow",
        )
        return
    if from_version == to_version:
        click.echo("You have latest config version. Nothing to migrate.")
        return
    migrated = make_migrations(common_config, from_version, to_version)
    if to_version == QualibrateConfig.version:
        QualibrateTopLevelConfig(migrated)
    with config_file.open("wb") as f_out:
        tomli_w.dump(migrated, f_out)


if __name__ == "__main__":
    migrate_command([], standalone_mode=False)
