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


def qualibrate_version_validator(
    config: RawConfigType,
    skip_if_none: bool = True,
) -> None:
    if not skip_if_none and QUALIBRATE_CONFIG_KEY not in config:
        raise InvalidQualibrateConfigVersion(
            "Qualibrate config has no 'qualibrate' key"
        )
    version = config[QUALIBRATE_CONFIG_KEY].get("version")
    if version is None or version != QualibrateConfig.version:
        raise InvalidQualibrateConfigVersion(
            "You have old version of config. "
            "Please run `qualibrate-config migrate`."
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
