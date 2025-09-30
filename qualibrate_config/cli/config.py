from copy import deepcopy
from pathlib import Path

import click
from click.exceptions import Exit

from qualibrate_config.cli.deprecated import (
    DeprecatedOption,
    DeprecatedOptionsCommand,
)
from qualibrate_config.cli.vars import (
    CALIBRATION_LIBRARY_FOLDER_HELP,
    CONFIG_PATH_HELP,
    QUAM_STATE_PATH_HELP,
    STORAGE_LOCATION_HELP,
)
from qualibrate_config.core.content import (
    get_config_file_content,
    simple_write,
    write_config,
)
from qualibrate_config.core.defaults import get_user_storage
from qualibrate_config.core.from_sources import (
    qualibrate_config_from_sources,
)
from qualibrate_config.models import PathSerializer
from qualibrate_config.models.qualibrate import QualibrateTopLevelConfig
from qualibrate_config.models.storage_type import StorageType
from qualibrate_config.qulibrate_types import RawConfigType
from qualibrate_config.validation import (
    validate_version_and_migrate_if_needed,
)
from qualibrate_config.vars import (
    DEFAULT_CONFIG_FILEPATH,
    QUALIBRATE_CONFIG_KEY,
    QUALIBRATE_PATH,
    QUAM_CONFIG_KEY,
    QUAM_STATE_PATH_CONFIG_KEY,
)

__all__ = ["config_command"]


@click.command(
    name="config",
    cls=DeprecatedOptionsCommand,
    help="Common config definition",
)
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
    "--password",
    "--qualibrate-password",
    type=str,
    default=None,
    cls=DeprecatedOption,
    deprecated=("--qualibrate-password",),
    preferred="--password",
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
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=get_user_storage(),
    show_default=True,
    help=STORAGE_LOCATION_HELP,
)
@click.option(
    "--calibration-library-resolver",
    "--runner-calibration-library-resolver",
    type=str,
    default="qualibrate.QualibrationLibrary",
    show_default=True,
    cls=DeprecatedOption,
    deprecated=("--runner-calibration-library-resolver",),
    preferred="--calibration-library-resolver",
    help=(
        "String contains python path to the class that represents qualibration "
        "library."
    ),
)
@click.option(
    "--calibration-library-folder",
    "--runner-calibration-library-folder",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=QUALIBRATE_PATH / "calibrations",
    show_default=True,
    cls=DeprecatedOption,
    deprecated=("--runner-calibration-library-folder",),
    preferred="--calibration-library-folder",
    help=CALIBRATION_LIBRARY_FOLDER_HELP,
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
    default="http://127.0.0.1:8001/execution/",
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
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Path to the frontend build static files.",
)
@click.option(
    "--spawn-qua-dashboards",
    type=bool,
    default=True,
    show_default=True,
    help=(
        "This flag indicates whether the `qua-dashboards` service should be "
        "started."
    ),
)
@click.option(
    "--quam-state-path",
    "--active-machine-path",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    cls=DeprecatedOption,
    required=False,
    deprecated=("--active-machine-path",),
    preferred="--quam-state-path",
    help=QUAM_STATE_PATH_HELP,
)
@click.option("--check-generator", is_flag=True, hidden=True)
@click.pass_context
def config_command(
    ctx: click.Context,
    config_path: Path,
    auto_accept: bool,
    project: str,
    log_folder: Path,
    password: str | None,
    storage_type: StorageType,
    storage_location: Path,
    calibration_library_resolver: str,
    calibration_library_folder: Path,
    spawn_runner: bool,
    runner_address: str,
    runner_timeout: float,
    spawn_app: bool,
    app_static_site_files: Path,
    spawn_qua_dashboards: bool,
    quam_state_path: Path | None,
    check_generator: bool,
) -> None:
    common_config, config_file = get_config_file_content(config_path)
    old_config = deepcopy(common_config)
    common_config, config_file = validate_version_and_migrate_if_needed(
        common_config, config_file
    )
    qualibrate_config = common_config.get(QUALIBRATE_CONFIG_KEY, {})
    required_subconfigs = ("storage",)
    optional_subconfigs = ("app", "runner", "composite", "calibration_library")
    qualibrate_config = qualibrate_config_from_sources(
        ctx,
        qualibrate_config,
        required_subconfigs,
        optional_subconfigs,
    )
    qs = QualibrateTopLevelConfig({QUALIBRATE_CONFIG_KEY: qualibrate_config})
    qs.qualibrate.storage.location.mkdir(parents=True, exist_ok=True)
    try:
        _temporary_fill_quam_state_path(common_config, quam_state_path)
        write_config(
            config_file,
            common_config,
            qs.qualibrate,
            QUALIBRATE_CONFIG_KEY,
            confirm=not auto_accept,
            check_generator=check_generator,
        )
    except Exit:
        if old_config:
            simple_write(config_file, old_config)
        raise


def _temporary_fill_quam_state_path(
    common_config: RawConfigType, state_path: Path | None
) -> RawConfigType:
    quam = common_config.setdefault(QUAM_CONFIG_KEY, {})
    active_machine = common_config.get("active_machine", {})
    new_state_path = (
        state_path
        or quam.get(QUAM_STATE_PATH_CONFIG_KEY)
        or active_machine.get("path")
    )
    if new_state_path is None:
        return common_config
    quam[QUAM_STATE_PATH_CONFIG_KEY] = PathSerializer.serialize_path(
        new_state_path
    )
    return common_config


if __name__ == "__main__":
    config_command([], standalone_mode=False)
