from collections.abc import Mapping
from pathlib import Path
from typing import (
    Any,
    Optional,
    TypeVar,
)

import click
from pydantic import ValidationError
from pydantic_settings import BaseSettings

from qualibrate_config.file import read_config_file

T = TypeVar(
    "T",
    bound=BaseSettings,
)

SUGGEST_MSG = (
    "Can't parse existing config. Fix it or overwrite "
    "by default values using `--overwrite` flag."
)


def get_config_solved_references_or_print_error(
    config_path: Path,
) -> Optional[dict[str, Any]]:
    try:
        return read_config_file(config_path, solve_references=True)
    except ValueError as ex:
        click.secho(str(ex), fg="red")
        click.secho(SUGGEST_MSG, fg="yellow")
    return None


def get_config_model_or_print_error(
    config: Mapping[str, Any],
    model_type: type[T],
    config_key: str,
) -> Optional[T]:
    try:
        return model_type(**config)
    except ValidationError as ex:
        errors = [
            (
                f"Message: {error.get('msg')}. "
                "Path: "
                f"{'.'.join([config_key, *map(str, error.get('loc', []))])}. "
                f"Value: {error.get('input')}"
            )
            for error in ex.errors()
        ]
        click.secho("\n".join(errors), fg="red")
        click.secho(SUGGEST_MSG, fg="yellow")
    return None
