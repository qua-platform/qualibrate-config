import sys
from pathlib import Path
from typing import Annotated

from qualibrate_config.models.base.config_base import BaseConfig
from qualibrate_config.models.base.default_value import DefaultConfigValue
from qualibrate_config.models.remote_services import (
    JsonTimelineDBRemoteServiceConfig,
)

__all__ = ["QualibrateAppConfig"]


def get_default_static_path() -> Path | None:
    """Locate the qualibrate frontend static files.

    Walks sys.path (CPython's list of directories where packages live) rather
    than relying on __file__ / find_spec().origin / importlib.resources, all
    of which Nuitka's custom loader corrupts with phantom paths in obfuscated
    builds. sys.path is maintained by CPython itself and Nuitka does not
    intercept it, so this lookup works identically for source and compiled
    installs.
    """
    for entry in sys.path:
        candidate = Path(entry) / "qualibrate" / "app" / "qualibrate_static"
        if candidate.is_dir():
            return candidate
    return None


class QualibrateAppConfig(BaseConfig):
    static_site_files: Annotated[
        Path | None, DefaultConfigValue(factory=get_default_static_path)
    ] = None

    timeline_db: JsonTimelineDBRemoteServiceConfig | None = None
