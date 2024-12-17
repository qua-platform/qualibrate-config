from pathlib import Path

from qualibrate_config.models.base.config_base import BaseConfig
from qualibrate_config.models.base.importable import Importable

__all__ = ["CalibrationLibraryConfig"]


class CalibrationLibraryConfig(BaseConfig):
    folder: Path

    resolver: Importable
