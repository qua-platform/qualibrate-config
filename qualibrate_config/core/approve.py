import os
from collections.abc import Mapping
from itertools import filterfalse
from pathlib import Path
from typing import Any

import click
from click.exceptions import Exit

from qualibrate_config.qulibrate_types import RawConfigType


def print_config(data: Mapping[str, Any], depth: int = 0) -> None:
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
        print_config(mapping_v, depth + 1)


def print_and_confirm(
    config_file: Path,
    exported_data: RawConfigType,
    check_generator: bool,
) -> None:
    click.echo(f"Config file path: {config_file}")
    click.echo(click.style("Generated config:", bold=True))
    print_config(exported_data)
    if check_generator:
        raise Exit(0)
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
        raise Exit(1)
