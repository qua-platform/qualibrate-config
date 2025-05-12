from pathlib import Path
from typing import (
    Any,
    Optional,
    TypeVar,
)

import click
from pydantic import ValidationError

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


def get_config_solved_references_or_print_error(
    config_path: Path,
) -> Optional[RawConfigType]:
    try:
        return read_config_file(config_path, solve_references=True)
    except ValueError as ex:
        click.secho(str(ex), fg="red")
        click.secho(SUGGEST_MSG, fg="yellow")
    return None


def get_config_model_or_print_error(
    config: RawConfigType,
    model_type: type[T],
    config_key: Optional[str],
) -> Optional[T]:
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
