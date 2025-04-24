from pathlib import Path
from typing import Optional

from qualibrate_config.models.base.config_base import BaseConfig
from qualibrate_config.models.remote_services import (
    JsonTimelineDBRemoteServiceConfig,
)

__all__ = ["QualibrateAppConfig"]


class QualibrateAppConfig(BaseConfig):
    static_site_files: Optional[Path] = None

    timeline_db: Optional[JsonTimelineDBRemoteServiceConfig] = None
