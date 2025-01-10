from pathlib import Path
from typing import Optional

from qualibrate_config.models.base.config_base import BaseConfig
from qualibrate_config.models.calibration_library import (
    CalibrationLibraryConfig,
)
from qualibrate_config.models.composite import QualibrateCompositeConfig
from qualibrate_config.models.q_app import QualibrateAppConfig
from qualibrate_config.models.remote_services import (
    QualibrateRunnerRemoteServiceConfig,
)
from qualibrate_config.models.storage import (
    StorageConfig,
)

__all__ = ["QualibrateConfig", "QualibrateTopLevelConfig"]


class QualibrateConfig(BaseConfig):
    version: int = 2
    project: str = "init_project"
    password: Optional[str] = None
    log_folder: Optional[Path] = None

    storage: StorageConfig
    app: Optional[QualibrateAppConfig] = None
    runner: Optional[QualibrateRunnerRemoteServiceConfig] = None
    composite: Optional[QualibrateCompositeConfig] = None
    calibration_library: Optional[CalibrationLibraryConfig] = None


class QualibrateTopLevelConfig(BaseConfig):
    qualibrate: QualibrateConfig
