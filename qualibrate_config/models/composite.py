from pathlib import Path
from typing import Annotated

from qualibrate_config.models.base.config_base import BaseConfig
from qualibrate_config.models.base.default_value import DefaultConfigValue
from qualibrate_config.models.q_app import get_default_static_path
from qualibrate_config.models.remote_services import (
    QuaDashboardSubServiceConfig,
    QualibrateAppSubServiceConfig,
    QualibrateRunnerSubServiceConfig,
)

__all__ = ["QualibrateCompositeConfig"]


class QualibrateCompositeConfig(BaseConfig):
    # `app`/`runner` spawn toggles are deprecated (no effect, see
    # `deprecated_subconfigs_validator`) and are no longer seeded by the
    # CLI, so they must be optional or a config without them fails to parse.
    app: QualibrateAppSubServiceConfig | None = None
    runner: QualibrateRunnerSubServiceConfig | None = None
    qua_dashboards: QuaDashboardSubServiceConfig
    static_site_files: Annotated[
        Path | None, DefaultConfigValue(factory=get_default_static_path)
    ] = None
