from abc import ABC, abstractmethod
from typing import Any


class MigrateBase(ABC):
    from_version: int
    to_version: int

    @staticmethod
    @abstractmethod
    def backward(data: dict[str, Any]) -> dict[str, Any]:
        pass

    @staticmethod
    @abstractmethod
    def forward(data: dict[str, Any]) -> dict[str, Any]:
        pass
