from pathlib import Path

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
    version: int = 5
    project: str = "init_project"
    password: str | None = None
    log_folder: Path | None = None

    storage: StorageConfig
    app: QualibrateAppConfig | None = None
    runner: QualibrateRunnerRemoteServiceConfig | None = None
    composite: QualibrateCompositeConfig | None = None
    calibration_library: CalibrationLibraryConfig | None = None


class QualibrateTopLevelConfig(BaseConfig):
    qualibrate: QualibrateConfig
