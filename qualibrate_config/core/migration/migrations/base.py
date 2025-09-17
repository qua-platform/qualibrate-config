from abc import ABC, abstractmethod
from pathlib import Path

from qualibrate_config.qulibrate_types import RawConfigType


class MigrateBase(ABC):
    from_version: int
    to_version: int

    @staticmethod
    @abstractmethod
    def backward(data: RawConfigType, config_path: Path) -> RawConfigType:
        pass

    @staticmethod
    @abstractmethod
    def forward(data: RawConfigType, config_path: Path) -> RawConfigType:
        pass
