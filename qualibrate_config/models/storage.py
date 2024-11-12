from pathlib import Path
from typing import ClassVar

from pydantic import DirectoryPath, field_serializer
from pydantic_core.core_schema import FieldSerializationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

from qualibrate_config.models.base.base_referenced_settings import \
    BaseReferencedSettings
from qualibrate_config.models.base.referenced_type import ModelReferencedType
from qualibrate_config.models.path_serializer import PathSerializer
from qualibrate_config.models.storage_type import StorageType
from qualibrate_config.vars import QUALIBRATE_STORAGE_SETTINGS_ENV_PREFIX

__all__ = ["StorageSettings", "StorageSettingsBase", "StorageSettingsSetup"]


class StorageSettingsBase(BaseReferencedSettings, PathSerializer):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix=QUALIBRATE_STORAGE_SETTINGS_ENV_PREFIX
    )

    type: StorageType = StorageType.local_storage
    location: ModelReferencedType[Path]


class StorageSettingsSetup(StorageSettingsBase):
    @field_serializer("type")
    def serialize_storage_type(
        self, value: StorageType, _info: FieldSerializationInfo
    ) -> str:
        return value.value

    location_serializer = field_serializer("location")(
        PathSerializer.serialize_path
    )


class StorageSettings(StorageSettingsBase):
    location: DirectoryPath
