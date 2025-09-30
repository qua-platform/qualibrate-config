from importlib.util import find_spec
from pathlib import Path
from typing import Annotated

from qualibrate_config.models.base.config_base import BaseConfig
from qualibrate_config.models.base.default_value import DefaultConfigValue
from qualibrate_config.models.remote_services import (
    JsonTimelineDBRemoteServiceConfig,
)

__all__ = ["QualibrateAppConfig"]


def get_default_static_path() -> Path | None:
    app_module = find_spec("qualibrate_app")
    if app_module is None or app_module.origin is None:
        return None
    return Path(app_module.origin).resolve().parents[1] / "qualibrate_static"


class QualibrateAppConfig(BaseConfig):
    static_site_files: Annotated[
        Path | None, DefaultConfigValue(factory=get_default_static_path)
    ] = None

    timeline_db: JsonTimelineDBRemoteServiceConfig | None = None
