import importlib
from typing import Callable

from qualibrate_config.qulibrate_types import RawConfigType


def migration_direction(from_version: int, to_version: int) -> bool:
    return to_version > from_version


def migration_functions(
    from_version: int,
    to_version: int,
    migrations_package: str,
    module_name_format: str,
) -> list[Callable[[RawConfigType], RawConfigType]]:
    direction = migration_direction(from_version, to_version)
    version_step = 1 if direction else -1
    versions = range(from_version, to_version, version_step)
    functions = []
    for version in versions:
        other_version = version + version_step
        minmax = (
            (version, other_version) if direction else (other_version, version)
        )
        module_name = module_name_format.format(minmax[0], minmax[1])
        module = importlib.import_module(f"{migrations_package}.{module_name}")
        function = (
            module.Migrate.forward if direction else module.Migrate.backward
        )
        functions.append(function)
    return functions


def make_migrations(
    data: RawConfigType,
    from_version: int,
    to_version: int,
    migrations_package: str = "qualibrate_config.cli.migrations",
    module_name_format: str = "v{}_v{}",
) -> RawConfigType:
    functions = migration_functions(
        from_version, to_version, migrations_package, module_name_format
    )
    for function in functions:
        data = function(data)
    return data
