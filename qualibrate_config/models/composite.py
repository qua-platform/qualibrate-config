from qualibrate_config.models.base.config_base import BaseConfig
from qualibrate_config.models.remote_services import (
    QualibrateAppSubServiceConfig,
    QualibrateRunnerSubServiceConfig,
)

__all__ = ["QualibrateCompositeConfig"]


class QualibrateCompositeConfig(BaseConfig):
    app: QualibrateAppSubServiceConfig
    runner: QualibrateRunnerSubServiceConfig
