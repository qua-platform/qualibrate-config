from pathlib import Path
from typing import (
    Any,
    TypeVar,
)

import click
from pydantic import ValidationError

from qualibrate_config.core.content import get_config_file_content
from qualibrate_config.core.migration.migrate import run_migrations
from qualibrate_config.file import read_config_file
from qualibrate_config.models import BaseConfig, QualibrateConfig
from qualibrate_config.qulibrate_types import RawConfigType
from qualibrate_config.vars import QUALIBRATE_CONFIG_KEY

T = TypeVar("T", bound=BaseConfig)

SUGGEST_MSG = (
    "Can't parse existing config. Fix it or overwrite "
    "by default values using `--overwrite` flag."
)


class WriteExitStatus(RuntimeError):
    def __init__(self, *args: Any, exit_code: int) -> None:
        super().__init__(*args)
        self.exit_code = exit_code


class InvalidQualibrateConfigVersion(RuntimeError):
    pass


class InvalidQualibrateConfigVersionError(InvalidQualibrateConfigVersion):
    def __init__(
        self,
        *args: Any,
        passed: Any = None,
        supported: int,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._passed_version = passed
        self._supported_version = supported

    def __str__(self) -> str:
        return (
            f"{super().__str__()} "
            f"Passed version: {self._passed_version}. "
            f"Supported version: {self._supported_version}"
        )

    @property
    def passed_version(self) -> Any:
        return self._passed_version

    @property
    def supported_version(self) -> int:
        return self._supported_version


class GreaterThanSupportedQualibrateConfigVersionError(
    InvalidQualibrateConfigVersionError
):
    pass


def qualibrate_version_validator(
    config: RawConfigType,
    skip_if_none: bool = True,
) -> None:
    if QUALIBRATE_CONFIG_KEY not in config:
        if skip_if_none:
            return
        raise InvalidQualibrateConfigVersionError(
            "Qualibrate config has no 'qualibrate' key",
            supported=QualibrateConfig.version,
        )
    version = config[QUALIBRATE_CONFIG_KEY].get("version")
    error_msg = (
        "QUAlibrate was unable to load the config. Can't parse version "
        "of qualibrate config. Please run `qualibrate-config config`."
    )
    if version is None:
        if skip_if_none:
            return
        raise InvalidQualibrateConfigVersionError(
            error_msg,
            passed=version,
            supported=QualibrateConfig.version,
        )
    if not isinstance(version, int):
        raise InvalidQualibrateConfigVersionError(
            error_msg,
            passed=version,
            supported=QualibrateConfig.version,
        )
    if version == QualibrateConfig.version:
        return
    if version < QualibrateConfig.version:
        raise InvalidQualibrateConfigVersionError(
            (
                "You have old version of config. "
                "Please run `qualibrate-config migrate`."
            ),
            passed=version,
            supported=QualibrateConfig.version,
        )
    raise GreaterThanSupportedQualibrateConfigVersionError(
        (
            "You have config version greater than supported. "
            "Please update your qualibrate-config package "
            "(pip install --upgrade qualibrate-config)."
        ),
        passed=version,
        supported=QualibrateConfig.version,
    )


def _no_longer_used_msg(path: str) -> str:
    return (
        f"'{path}' is deprecated and will no longer be used starting with "
        "QUAlibrate 1.5.0. It is preserved in your config file but will "
        "have no effect from that version onward."
    )


# Only exact leaf/subtree paths that are actually retired are listed here —
# not the whole `app`/`runner` namespaces, since those may gain new,
# unrelated settings in the future.
# TODO: Remove in qualibrate-config 0.2, along with the fields/models
# this validator warns about (see qualibrate_config/models/composite.py
# and qualibrate_config/models/remote_services.py). Write a migration
# that strips these unsupported entries (runner.address, runner.timeout,
# app.static_site_files, composite.app, composite.runner,
# composite.qua_dashboards) from existing config files instead of silently
# ignoring them.
DEPRECATED_SUBCONFIGS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("runner", "address"), _no_longer_used_msg("runner.address")),
    (("runner", "timeout"), _no_longer_used_msg("runner.timeout")),
    (
        ("app", "static_site_files"),
        "'app.static_site_files' is deprecated in favor of "
        "'composite.static_site_files' and will no longer be read starting "
        "with QUAlibrate 1.5.0.",
    ),
    (("composite", "app"), _no_longer_used_msg("composite.app")),
    (("composite", "runner"), _no_longer_used_msg("composite.runner")),
    (
        ("composite", "qua_dashboards"),
        _no_longer_used_msg("composite.qua_dashboards"),
    ),
)


def _path_present(data: RawConfigType, path: tuple[str, ...]) -> bool:
    node: Any = data
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return False
        node = node[key]
    return True


# Paths already warned about in this process, so that each deprecated path
# is only warned about once even if `deprecated_subconfigs_validator` is
# invoked multiple times (e.g. once per config load). Note this dedups by
# path across *all* configs validated in the process, not per config file —
# fine for the one-config-per-invocation CLI, but worth knowing in a
# long-lived process that validates multiple distinct configs.
_WARNED_DEPRECATED_SUBCONFIGS: set[tuple[str, ...]] = set()


def deprecated_subconfigs_validator(config: RawConfigType) -> None:
    qualibrate = config.get(QUALIBRATE_CONFIG_KEY, {})
    for path, message in DEPRECATED_SUBCONFIGS:
        if path in _WARNED_DEPRECATED_SUBCONFIGS:
            continue
        if _path_present(qualibrate, path):
            _WARNED_DEPRECATED_SUBCONFIGS.add(path)
            click.secho(message, fg="yellow")


def validate_version_and_migrate_if_needed(
    common_config: dict[str, Any],
    config_path: Path,
) -> tuple[dict[str, Any], Path]:
    try:
        qualibrate_version_validator(common_config, False)
    except GreaterThanSupportedQualibrateConfigVersionError as ex:
        error_msg = (
            f"QUAlibrate was unable to load the config. {str(ex)}. If this "
            f'problem persists, please delete "{config_path}" and retry '
            'running "qualibrate config"'
        )
        raise RuntimeError(error_msg) from ex
    except InvalidQualibrateConfigVersionError:
        if common_config:
            run_migrations(config_path)
            return get_config_file_content(config_path)
    return common_config, config_path


def get_config_solved_references_or_print_error(
    config_path: Path,
) -> RawConfigType | None:
    try:
        return read_config_file(config_path, solve_references=True)
    except ValueError as ex:
        click.secho(str(ex), fg="red")
        click.secho(SUGGEST_MSG, fg="yellow")
    return None


def get_config_model_or_print_error(
    config: RawConfigType,
    model_type: type[T],
    config_key: str | None,
) -> T | None:
    try:
        return model_type(config)
    except ValidationError as ex:
        prefix = [config_key] if config_key else []
        errors = [
            (
                f"Message: {error.get('msg')}. "
                "Path: "
                f"{'.'.join([*prefix, *map(str, error.get('loc', []))])}. "
                f"Value: {error.get('input')}"
            )
            for error in ex.errors()
        ]
        click.secho("\n".join(errors), fg="red")
        click.secho(SUGGEST_MSG, fg="yellow")
    return None
