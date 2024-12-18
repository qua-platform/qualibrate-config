import os
import sys
from collections.abc import Mapping
from importlib.util import find_spec
from itertools import filterfalse
from pathlib import Path
from typing import Any, Optional

import click
import tomli_w
from click.core import ParameterSource

from qualibrate_config.cli.utils.defaults import get_user_storage, \
    get_qapp_static_file_path
from qualibrate_config.cli.utils.from_sources import config_from_sources
from qualibrate_config.file import get_config_file
from qualibrate_config.models import QualibrateConfig
from qualibrate_config.models.storage_type import StorageType
from qualibrate_config.models.qualibrate import QualibrateTopLevelConfig
from qualibrate_config.references.resolvers import resolve_references
from qualibrate_config.vars import (
    QUALIBRATE_CONFIG_KEY, QUALIBRATE_PATH, DEFAULT_CONFIG_FILENAME
)

if sys.version_info[:2] < (3, 11):
    import tomli as tomllib
else:
    import tomllib

__all__ = ["config_command"]


def get_config(config_path: Path) -> tuple[dict[str, Any], Path]:
    """Returns config and path to file"""
    config_file = get_config_file(
        config_path, DEFAULT_CONFIG_FILENAME, raise_not_exists=False
    )
    if config_file.is_file():
        return tomllib.loads(config_file.read_text()), config_path
    return {}, config_file


def _print_config(data: Mapping[str, Any], depth: int = 0) -> None:
    if not len(data.keys()):
        return
    max_key_len = max(map(len, map(str, data.keys())))
    non_mapping_items = list(
        filterfalse(lambda item: isinstance(item[1], Mapping), data.items())
    )
    if len(non_mapping_items):
        click.echo(
            os.linesep.join(
                f"{' ' * 4 * depth}{f'{k} :':<{max_key_len + 3}} {v}"
                for k, v in non_mapping_items
            )
        )
    mappings = filter(lambda x: isinstance(x[1], Mapping), data.items())
    for mapping_k, mapping_v in mappings:
        click.echo(f"{' ' * 4 * depth}{mapping_k} :")
        _print_config(mapping_v, depth + 1)


def _print_and_confirm(
    config_file: Path,
    exported_data: dict[str, Any],
    check_generator: bool,
) -> None:
    click.echo(f"Config file path: {config_file}")
    click.echo(click.style("Generated config:", bold=True))
    _print_config(exported_data)
    if check_generator:
        exit(0)
    confirmed = click.confirm("Do you confirm config?", default=True)
    if not confirmed:
        click.echo(
            click.style(
                (
                    "The configuration has not been confirmed. "
                    "Rerun config script."
                ),
                fg="yellow",
            )
        )
        exit(1)


def write_config(
    config_file: Path,
    common_config: dict[str, Any],
    qs: QualibrateConfig,
    confirm: bool = True,
    check_generator: bool = False,
) -> None:
    exported_data = qs.serialize(exclude_none=True)
    common_config[QUALIBRATE_CONFIG_KEY] = exported_data
    if confirm or check_generator:
        _print_and_confirm(config_file, common_config, check_generator)
    if qs.project in qs.storage.location.parts:
        qs.storage.location.mkdir(parents=True, exist_ok=True)
    else:
        (qs.storage.location / qs.project).mkdir(parents=True, exist_ok=True)
    if not config_file.parent.exists():
        config_file.parent.mkdir(parents=True)
    with config_file.open("wb") as f_out:
        tomli_w.dump(common_config, f_out)


@click.command(name="config")
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
@click.option(
    "--auto-accept",
    type=bool,
    is_flag=True,
    default=False,
    show_default=True,
    help=(
        "Flag responsible for whether to skip confirmation of the generated "
        "config."
    ),
)
@click.option(
    "--project",
    type=str,
    default="init_project",
    show_default=True,
    help=(
        "The name of qualibrate app project that will be used for storing runs "
        "results and resolving them."
    ),
)
@click.option(
    "--log-folder",
    type=click.Path(file_okay=False, resolve_path=True, path_type=Path),
    default=QUALIBRATE_PATH / "logs",
    help="The path to the directory where the logs should be stored to.",
    show_default=True,
)
@click.option(
    "--qualibrate-password",
    type=str,
    default=None,
    help=(
        "Password used to authorize users. By default, no password is used. "
        "Everyone has access to the API. If a password is specified during "
        "configuration, you must log in to access the API."
    ),
)
@click.option(
    "--storage-type",
    type=click.Choice([t.value for t in StorageType]),
    default="local_storage",
    show_default=True,
    callback=lambda ctx, param, value: StorageType(value),
    help=(
        "Type of storage. Only `local_storage` is supported now. Use specified "
        "local path as the database."
    ),
)
@click.option(
    "--storage-location",
    type=click.Path(file_okay=False, dir_okay=True),
    default=get_user_storage(),
    show_default=True,
    help=(
        "Path to the local user storage. Used for storing nodes output data."
    ),
)
@click.option(
    "--calibration-library-resolver",
    type=str,
    default="qualibrate.QualibrationLibrary",
    show_default=True,
    help=(
        "String contains python path to the class that represents qualibration "
        "library."
    ),
)
@click.option(
    "--calibration-library-folder",
    type=click.Path(file_okay=False, dir_okay=True),
    default=QUALIBRATE_PATH / "calibrations",
    show_default=True,
    help="Path to the folder contains calibration nodes and graphs.",
)
@click.option(
    "--spawn-runner",
    type=bool,
    default=True,
    show_default=True,
    help=(
        "This flag indicates whether the `qualibrate-runner` service should be "
        "started. This service is designed to run nodes and graphs. The service"
        " can be spawned independently."
    ),
)
@click.option(
    "--runner-address",
    type=str,  # TODO: add type check for addr
    default="http://localhost:8001/execution/",
    show_default=True,
    help=(
        "Address of `qualibrate-runner` service. If the service is spawned by "
        "the `qualibrate` then the default address should be kept as is. If you"
        " are running the service separately, you must specify its address."
    ),
)
@click.option(
    "--runner-timeout",
    type=float,
    default=1.0,
    show_default=True,
    help=(
        "Maximum waiting time for a response from the `qualibrate-runner` "
        "service."
    ),
)
@click.option(
    "--spawn-app",
    type=bool,
    default=True,
    show_default=True,
    help=(
        "This flag indicates whether the `qualibrate-app` service should be "
        "started. This service is designed to getting info about snapshots. "
        "The service can be spawned independently."
    ),
)
@click.option(
    "--app-static-site-files",
    type=click.Path(file_okay=False, dir_okay=True),
    default=get_qapp_static_file_path(),
    show_default=True,
    help="Path to the frontend build static files.",
)
@click.option("--check-generator", is_flag=True, hidden=True)
@click.pass_context
def config_command(
    ctx: click.Context,
    config_path: Path,
    auto_accept: bool,
    project: str,
    log_folder: Path,
    qualibrate_password: Optional[str],
    storage_type: StorageType,
    storage_location: Path,
    calibration_library_resolver: str,
    calibration_library_folder: Path,
    spawn_runner: bool,
    runner_address: str,
    runner_timeout: float,
    spawn_app: bool,
    app_static_site_files: Path,
    check_generator: bool,
) -> None:
    common_config, config_file = get_config(config_path)
    qualibrate_config = common_config.get(QUALIBRATE_CONFIG_KEY, {})
    required_subconfigs = ("storage",)
    optional_subconfigs = ("app", "runner", "composite", "calibration_library")
    qualibrate_config = config_from_sources(
        ctx,
        qualibrate_config,
        required_subconfigs,
        optional_subconfigs,
    )
    qs = QualibrateTopLevelConfig({QUALIBRATE_CONFIG_KEY: qualibrate_config})
    qs.qualibrate.storage.location.mkdir(parents=True, exist_ok=True)
    write_config(
        config_file,
        common_config,
        qs.qualibrate,
        confirm=not auto_accept,
        check_generator=check_generator,
    )


if __name__ == "__main__":
    config_command(
        [],
        standalone_mode=False
    )
