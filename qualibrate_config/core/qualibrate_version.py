import re
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

__all__ = ["qualibrate_supports_single_backend"]

# TODO: Remove along with the rest of the `composite.app`/`composite.runner`
# spawn-seeding fallback once qualibrate<1.5.0 no longer needs to be
# supported (see `_get_composite_config` in `core/from_sources.py`).
SINGLE_BACKEND_MIN_QUALIBRATE_VERSION = (1, 5, 0)

_LEADING_VERSION_RE = re.compile(r"(\d+(?:\.\d+)*)")


def _parse_version_tuple(raw: str) -> tuple[int, ...] | None:
    match = _LEADING_VERSION_RE.match(raw)
    if not match:
        return None
    return tuple(int(part) for part in match.group(1).split("."))


def qualibrate_supports_single_backend() -> bool:
    """
    Whether the installed `qualibrate` package is new enough (>=1.5.0) to
    no longer require the deprecated `composite.app`/`composite.runner`
    spawn toggles.

    Returns `False` (i.e. assumes an old, pre-single-backend qualibrate)
    if `qualibrate` isn't installed alongside qualibrate-config or its
    version can't be parsed. Seeding the deprecated spawn fields is
    harmless for a modern qualibrate, but omitting them breaks
    qualibrate<1.5.0, which does `composite.runner.spawn` and raises
    `AttributeError: 'NoneType' object has no attribute 'spawn'` when
    that subconfig is absent.
    """
    try:
        raw = _pkg_version("qualibrate")
    except PackageNotFoundError:
        return False
    parsed = _parse_version_tuple(raw)
    if parsed is None:
        return False
    return parsed >= SINGLE_BACKEND_MIN_QUALIBRATE_VERSION
