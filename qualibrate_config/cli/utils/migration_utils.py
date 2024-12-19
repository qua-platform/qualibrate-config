import importlib
from typing import Any, Callable


def migration_direction(from_version: int, to_version: int) -> bool:
    return to_version > from_version


def migration_functions(
    from_version: int, to_version: int
) -> list[Callable[[dict[str, Any]], dict[str, Any]]]:
    direction = migration_direction(from_version, to_version)
    version_step = 1 if direction else -1
    versions = range(from_version, to_version, version_step)
    functions = []
    for version in versions:
        other_version = version + version_step
        minmax = (
            (version, other_version) if direction else (other_version, version)
        )
        module_name = f"v{minmax[0]}_v{minmax[1]}"
        module = importlib.import_module(
            f"qualibrate_config.cli.migrations.{module_name}"
        )
        function = (
            module.Migrate.forward if direction else module.Migrate.backward
        )
        functions.append(function)
    return functions


def make_migrations(
    data: dict[str, Any], from_version: int, to_version: int
) -> dict[str, Any]:
    functions = migration_functions(from_version, to_version)
    for function in functions:
        data = function(data)
    return data
