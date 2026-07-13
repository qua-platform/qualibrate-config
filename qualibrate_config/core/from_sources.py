from typing import cast

import click
from click.core import ParameterSource

from qualibrate_config.core.qualibrate_version import (
    qualibrate_supports_single_backend,
)
from qualibrate_config.qulibrate_types import RawConfigType

__all__ = [
    "not_default",
    "get_config_by_args_mapping",
    "get_optional_config",
    "get_config_by_args_mapping_only_if_passed",
    "get_optional_config_only_if_passed",
    "qualibrate_config_from_sources",
]


def not_default(ctx: click.Context, arg_key: str) -> bool:
    return ctx.get_parameter_source(arg_key) in (
        ParameterSource.COMMANDLINE,
        ParameterSource.ENVIRONMENT,
    )


def get_config_by_args_mapping(
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


def get_optional_config(
    args_mapping: dict[str, str],
    from_file: RawConfigType | None,
    ctx: click.Context,
) -> RawConfigType | None:
    return get_config_by_args_mapping(args_mapping, from_file or {}, ctx)


def get_config_by_args_mapping_only_if_passed(
    args_mapping: dict[str, str],
    from_file: RawConfigType,
    ctx: click.Context,
) -> RawConfigType:
    """Like `get_config_by_args_mapping`, but never seeds a default value
    into a config that doesn't already have it — only an explicitly passed
    CLI/env value is written. Used for deprecated options that should stop
    appearing in freshly generated configs."""
    params = list(
        filter(lambda item: item[0] in args_mapping, ctx.params.items())
    )
    for arg_key, arg_value in params:
        if not_default(ctx, arg_key):
            from_file[args_mapping[arg_key]] = arg_value
    return from_file


def get_optional_config_only_if_passed(
    args_mapping: dict[str, str],
    from_file: RawConfigType | None,
    ctx: click.Context,
) -> RawConfigType:
    return get_config_by_args_mapping_only_if_passed(
        args_mapping, from_file or {}, ctx
    )


def _get_storage_config(
    ctx: click.Context, from_file: RawConfigType
) -> RawConfigType:
    storage_keys = {
        "storage_type": "type",
        "storage_location": "location",
    }
    return get_config_by_args_mapping(storage_keys, from_file, ctx)


def _get_calibration_library_config(
    ctx: click.Context, from_file: RawConfigType | None
) -> RawConfigType | None:
    args_mapping = {
        "calibration_library_resolver": "resolver",
        "calibration_library_folder": "folder",
    }
    from_file = get_optional_config(args_mapping, from_file, ctx)
    return from_file


def _get_app_config(
    ctx: click.Context, from_file: RawConfigType
) -> RawConfigType | None:
    # `static_site_files` is deprecated in favor of
    # `composite.static_site_files` (see `_get_composite_config`) — don't
    # seed defaults into new configs, only carry through an explicitly
    # passed or pre-existing value.
    args_mapping = {"app_static_site_files": "static_site_files"}
    # TODO: JsonTimelineDB
    return get_optional_config_only_if_passed(args_mapping, from_file, ctx)


def _get_runner_config(
    ctx: click.Context, from_file: RawConfigType
) -> RawConfigType | None:
    # `address`/`timeout` are deprecated (no effect on qualibrate>=1.5.0) —
    # don't seed defaults into new configs, only carry through an explicitly
    # passed value. Exception: qualibrate<1.5.0 reads these fields directly
    # from the config and raises if they're absent, so seed the old defaults
    # for those installations.
    args_mapping = {"runner_address": "address", "runner_timeout": "timeout"}
    result = get_optional_config_only_if_passed(args_mapping, from_file, ctx)
    if not qualibrate_supports_single_backend():
        result.setdefault("address", "http://127.0.0.1:8001/execution/")
        result.setdefault("timeout", 1.0)
    return result


def _get_composite_config(
    ctx: click.Context, from_file: RawConfigType | None
) -> RawConfigType | None:
    # `app`/`runner`/`qua_dashboards` spawn toggles are deprecated (no
    # effect) — don't seed defaults into new configs, only carry through an
    # explicitly passed or pre-existing value. The one exception: if the
    # installed `qualibrate` is older than 1.5.0 (or its version can't be
    # determined), it still requires these subconfigs to be present, so
    # default `spawn=True` for it below.
    # TODO: Remove this fallback once qualibrate<1.5.0 no longer needs to
    # be supported (see `qualibrate_supports_single_backend`).
    app = get_optional_config_only_if_passed(
        {"spawn_app": "spawn"},
        from_file.get("app") if from_file is not None else None,
        ctx,
    )
    runner = get_optional_config_only_if_passed(
        {"spawn_runner": "spawn"},
        from_file.get("runner") if from_file is not None else None,
        ctx,
    )
    qua_dashboards = get_optional_config_only_if_passed(
        {"spawn_qua_dashboards": "spawn"},
        from_file.get("qua_dashboards") if from_file is not None else None,
        ctx,
    )
    if not qualibrate_supports_single_backend():
        app.setdefault("spawn", True)
        runner.setdefault("spawn", True)
        qua_dashboards.setdefault("spawn", True)
    result = get_optional_config_only_if_passed(
        {"static_site_files": "static_site_files"}, from_file, ctx
    )
    if app:
        result["app"] = app
    if runner:
        result["runner"] = runner
    if qua_dashboards:
        result["qua_dashboards"] = qua_dashboards
    return result


def qualibrate_config_from_sources(
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
        "password": "password",
        "version": "version",
        "project": "project",
        "log_folder": "log_folder",
    }
    qualibrate_common = get_config_by_args_mapping(
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
