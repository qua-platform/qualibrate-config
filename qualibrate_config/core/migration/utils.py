import importlib
from collections.abc import Callable
from pathlib import Path
from typing import cast

from qualibrate_config.core.migration.migrations.base import MigrateBase
from qualibrate_config.qulibrate_types import RawConfigType

__all__ = ["migration_direction", "migration_functions", "make_migrations"]


def migration_direction(from_version: int, to_version: int) -> bool:
    return to_version > from_version


def migration_functions(
    from_version: int,
    to_version: int,
    migrations_package: str,
    module_name_format: str,
) -> list[
    Callable[[RawConfigType, Path], RawConfigType]
    | Callable[[RawConfigType], RawConfigType]
]:
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
        full_module_name = f"{migrations_package}.{module_name}"
        module = importlib.import_module(full_module_name)
        if not hasattr(module, "Migrate") or not issubclass(
            module.Migrate, MigrateBase
        ):
            raise AttributeError(
                f"Module {full_module_name} has no Migrate class or it "
                f"has invalid hierarchy"
            )
        function = (
            module.Migrate.forward if direction else module.Migrate.backward
        )
        functions.append(function)
    return functions


def make_migrations(
    data: RawConfigType,
    from_version: int,
    to_version: int,
    migrations_package: str = "qualibrate_config.core.migration.migrations",
    module_name_format: str = "v{}_v{}",
    *,
    config_path: Path | None = None,
) -> RawConfigType:
    functions = migration_functions(
        from_version, to_version, migrations_package, module_name_format
    )
    for function in functions:
        if function.__code__.co_argcount == 1:
            data = cast(Callable[[RawConfigType], RawConfigType], function)(
                data
            )
        else:
            if config_path is None:
                raise RuntimeError("Config path must be provided")
            data = cast(
                Callable[[RawConfigType, Path], RawConfigType], function
            )(data, config_path)
    return data
