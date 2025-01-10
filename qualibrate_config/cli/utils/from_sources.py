from typing import Optional, cast

import click
from click.core import ParameterSource

from qualibrate_config.qulibrate_types import RawConfigType


def not_default(ctx: click.Context, arg_key: str) -> bool:
    return ctx.get_parameter_source(arg_key) in (
        ParameterSource.COMMANDLINE,
        ParameterSource.ENVIRONMENT,
    )


def _get_config(
    args_mapping: dict[str, str],
    from_file: RawConfigType,
    ctx: click.Context,
) -> RawConfigType:
    params = list(
        filter(lambda item: item[0] in args_mapping, ctx.params.items())
    )
    for arg_key, arg_value in params:
        not_default_resolver_arg = not_default(ctx, arg_key)
        if not_default_resolver_arg or args_mapping[arg_key] not in from_file:
            from_file[args_mapping[arg_key]] = arg_value
    return from_file


def _get_optional_config(
    args_mapping: dict[str, str],
    from_file: Optional[RawConfigType],
    ctx: click.Context,
) -> Optional[RawConfigType]:
    return _get_config(args_mapping, from_file or {}, ctx)


def _get_storage_config(
    ctx: click.Context, from_file: RawConfigType
) -> RawConfigType:
    storage_keys = {
        "storage_type": "type",
        "storage_location": "location",
    }
    return _get_config(storage_keys, from_file, ctx)


def _get_calibration_library_config(
    ctx: click.Context, from_file: Optional[RawConfigType]
) -> Optional[RawConfigType]:
    args_mapping = {
        "calibration_library_resolver": "resolver",
        "calibration_library_folder": "folder",
    }
    from_file = _get_optional_config(args_mapping, from_file, ctx)
    return from_file


def _get_app_config(
    ctx: click.Context, from_file: RawConfigType
) -> Optional[RawConfigType]:
    args_mapping = {"app_static_site_files": "static_site_files"}
    # TODO: JsonTimelineDB
    return _get_optional_config(args_mapping, from_file, ctx)


def _get_runner_config(
    ctx: click.Context, from_file: RawConfigType
) -> Optional[RawConfigType]:
    args_mapping = {"runner_address": "address", "runner_timeout": "timeout"}
    return _get_optional_config(args_mapping, from_file, ctx)


def _get_composite_config(
    ctx: click.Context, from_file: Optional[RawConfigType]
) -> Optional[RawConfigType]:
    app = _get_optional_config(
        {"spawn_app": "spawn"},
        from_file.get("app") if from_file is not None else None,
        ctx,
    )
    runner = _get_optional_config(
        {"spawn_runner": "spawn"},
        from_file.get("runner") if from_file is not None else None,
        ctx,
    )
    if app is None and runner is None:
        return None
    return {
        "app": (app or {"spawn": False}),
        "runner": (runner or {"spawn": False}),
    }


def config_from_sources(
    ctx: click.Context,
    from_file: RawConfigType,
    required_subconfigs: tuple[str, ...],
    optional_subconfig_names: tuple[str, ...],
) -> RawConfigType:
    for subconfig in required_subconfigs:
        if subconfig not in from_file:
            from_file[subconfig] = {}
    optional_configs_from_sources = {
        "calibration_library": _get_calibration_library_config,
        "app": _get_app_config,
        "runner": _get_runner_config,
        "composite": _get_composite_config,
    }
    optional_subconfigs = {
        name: optional_configs_from_sources[name](
            ctx, cast(RawConfigType, from_file.get(name))
        )
        for name in optional_subconfig_names
    }
    storage_config = _get_storage_config(ctx, from_file["storage"])
    qualibrate_common_mapping = {
        "qualibrate_password": "password",
        "version": "version",
        "project": "project",
        "log_folder": "log_folder",
    }
    qualibrate_common = _get_config(
        qualibrate_common_mapping,
        from_file,
        ctx,
    )
    qualibrate_common.update(
        {
            "storage": storage_config,
            **optional_subconfigs,
        }
    )
    return qualibrate_common
