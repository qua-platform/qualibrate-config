from typing import Optional

from qualibrate_config.cli.migrations.base import MigrateBase
from qualibrate_config.cli.utils.defaults import get_qua_dashboards_spawn
from qualibrate_config.qulibrate_types import RawConfigType


class Migrate(MigrateBase):
    from_version: int = 2
    to_version: int = 3

    @staticmethod
    def backward(data: RawConfigType) -> RawConfigType:
        qualibrate = data.pop("qualibrate")
        assert qualibrate.pop("version") == Migrate.to_version
        qualibrate["version"] = Migrate.from_version

        composite: Optional[RawConfigType] = qualibrate.pop("composite", None)
        if composite:
            composite.pop("qua_dashboards", None)

        return {
            "qualibrate": qualibrate,
            **data,
        }

    @staticmethod
    def forward(data: RawConfigType) -> RawConfigType:
        new_qualibrate = data.pop("qualibrate")
        version = new_qualibrate.pop("version")
        assert version == Migrate.from_version
        if composite := new_qualibrate.get("composite", None):
            composite.update(
                {"qua_dashboards": {"spawn": get_qua_dashboards_spawn()}}
            )
        new_qualibrate["version"] = Migrate.to_version
        new_data = {"qualibrate": new_qualibrate, **data}
        return new_data
