from functools import cached_property

from qualibrate_config.models.base.config_base import BaseConfig

__all__ = [
    "RemoteServiceBaseConfig",
    "SpawnServiceBaseConfig",
    "JsonTimelineDBRemoteServiceConfig",
    "QualibrateRunnerRemoteServiceConfig",
    "QualibrateAppSubServiceConfig",
    "QualibrateRunnerSubServiceConfig",
    "QuaDashboardSubServiceConfig",
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


class QualibrateRunnerRemoteServiceConfig(BaseConfig):
    # `address`/`timeout` are deprecated and have no effect (see
    # `deprecated_subconfigs_validator`); kept optional (rather than
    # inheriting `RemoteServiceBaseConfig`'s required fields) so the
    # `runner` block can still be reused for future, unrelated settings
    # without requiring these two to be present.
    address: str | None = None
    timeout: float | None = None

    @cached_property
    def address_with_root(self) -> str:
        address = str(self.address)
        return address if address.endswith("/") else address + "/"


class QualibrateAppSubServiceConfig(SpawnServiceBaseConfig):
    pass


class QualibrateRunnerSubServiceConfig(SpawnServiceBaseConfig):
    pass


class QuaDashboardSubServiceConfig(SpawnServiceBaseConfig):
    pass
