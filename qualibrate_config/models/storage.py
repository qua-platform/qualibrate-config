from pathlib import Path

from qualibrate_config.models.base.config_base import BaseConfig
from qualibrate_config.models.storage_type import StorageType

__all__ = ["StorageConfig"]


class StorageConfig(BaseConfig):
    type: StorageType = StorageType.local_storage
    location: Path
