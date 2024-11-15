from pathlib import Path
from typing import ClassVar, Optional

from pydantic import field_serializer
from pydantic_core.core_schema import FieldSerializationInfo
from pydantic_settings import SettingsConfigDict

from qualibrate_config.models.base.base_referenced_settings import (
    BaseReferencedSettings,
)
from qualibrate_config.models.base.referenced_type import ModelReferencedType
from qualibrate_config.models.storage import (
    StorageSettings,
    StorageSettingsBase,
    StorageSettingsSetup,
)
from qualibrate_config.models.versioned import Versioned
from qualibrate_config.vars import QUALIBRATE_SETTINGS_ENV_PREFIX

__all__ = [
    "QualibrateSettings",
    "QualibrateSettingsBase",
    "QualibrateSettingsSetup",
]


class QualibrateSettingsBase(BaseReferencedSettings, Versioned):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        extra="ignore",
        env_prefix=QUALIBRATE_SETTINGS_ENV_PREFIX,
    )

    project: Optional[str]
    storage: StorageSettingsBase
    log_folder: Optional[ModelReferencedType[Path]] = None


class QualibrateSettingsSetup(QualibrateSettingsBase):
    storage: StorageSettingsSetup

    @field_serializer("project")
    def serialize_project(
        self, value: Optional[str], _info: FieldSerializationInfo
    ) -> str:
        return value or ""


class QualibrateSettings(QualibrateSettingsBase):
    project: str
    storage: StorageSettings
