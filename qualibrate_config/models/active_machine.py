from pathlib import Path
from typing import ClassVar, Optional

from pydantic import field_serializer
from pydantic_settings import SettingsConfigDict

from qualibrate_config.models.base.base_referenced_settings import \
    BaseReferencedSettings
from qualibrate_config.models.path_serializer import PathSerializer
from qualibrate_config.vars import ACTIVE_MACHINE_SETTINGS_ENV_PREFIX

__all__ = [
    "ActiveMachineSettings",
    "ActiveMachineSettingsBase",
    "ActiveMachineSettingsSetup",
]


class ActiveMachineSettingsBase(BaseReferencedSettings, PathSerializer):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix=ACTIVE_MACHINE_SETTINGS_ENV_PREFIX
    )

    path: Optional[Path] = None


class ActiveMachineSettingsSetup(ActiveMachineSettingsBase):
    path_serializer = field_serializer("path")(PathSerializer.serialize_path)


class ActiveMachineSettings(ActiveMachineSettingsBase):
    # path: DirectoryPath # TODO: require directory
    pass
