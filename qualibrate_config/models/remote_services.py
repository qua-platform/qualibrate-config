from functools import cached_property

from qualibrate_config.models.base.config_base import BaseConfig

__all__ = [
    "RemoteServiceBaseConfig",
    "SpawnServiceBaseConfig",
    "JsonTimelineDBRemoteServiceConfig",
    "QualibrateRunnerRemoteServiceConfig",
    "QualibrateAppSubServiceConfig",
    "QualibrateRunnerSubServiceConfig",
]


class RemoteServiceBaseConfig(BaseConfig):
    address: str
    timeout: float

    @cached_property
    def address_with_root(self) -> str:
        address = str(self.address)
        return address if address.endswith("/") else address + "/"


class SpawnServiceBaseConfig(BaseConfig):
    spawn: bool


class JsonTimelineDBRemoteServiceConfig(RemoteServiceBaseConfig):
    pass


class QualibrateRunnerRemoteServiceConfig(RemoteServiceBaseConfig):
    pass


class QualibrateAppSubServiceConfig(SpawnServiceBaseConfig):
    pass


class QualibrateRunnerSubServiceConfig(SpawnServiceBaseConfig):
    pass
