from abc import ABC, abstractmethod

from qualibrate_config.qulibrate_types import RawConfigType


class MigrateBase(ABC):
    from_version: int
    to_version: int

    @staticmethod
    @abstractmethod
    def backward(data: RawConfigType) -> RawConfigType:
        pass

    @staticmethod
    @abstractmethod
    def forward(data: RawConfigType) -> RawConfigType:
        pass
