from pathlib import Path

import click
import tomli_w

from qualibrate_config.core.content import get_config_file_content
from qualibrate_config.core.migration.utils import make_migrations
from qualibrate_config.models import QualibrateConfig
from qualibrate_config.models.qualibrate import QualibrateTopLevelConfig
from qualibrate_config.vars import QUALIBRATE_CONFIG_KEY

__all__ = ["run_migrations"]


def run_migrations(
    config_path: Path, to_version: int = QualibrateConfig.version
) -> None:
    common_config, config_file = get_config_file_content(config_path)
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
    if from_version > to_version:
        # TODO: merge with `qualibrate_version_validator`
        click.secho(
            (
                f"You have config version ({from_version}) greater than "
                f"supported ({QualibrateConfig.version}). Please update your "
                f"qualibrate-config package (pip install --upgrade "
                f"qualibrate-config)."
            ),
            fg="yellow",
        )
        return
    migrated = make_migrations(
        common_config, from_version, to_version, config_path=config_file
    )
    if to_version == QualibrateConfig.version:
        QualibrateTopLevelConfig(migrated)
    with config_file.open("wb") as f_out:
        tomli_w.dump(migrated, f_out)
