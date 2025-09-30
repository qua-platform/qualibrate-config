from copy import deepcopy
from pathlib import Path

from qualibrate_config.core.migration.migrations.base import MigrateBase
from qualibrate_config.qulibrate_types import RawConfigType


class Migrate(MigrateBase):
    from_version: int = 2
    to_version: int = 3

    @staticmethod
    def backward(data: RawConfigType, config_path: Path) -> RawConfigType:
        data = deepcopy(data)
        qualibrate = data.pop("qualibrate")
        assert qualibrate.pop("version") == Migrate.to_version
        qualibrate["version"] = Migrate.from_version

        composite: RawConfigType | None = qualibrate.get("composite", None)
        if composite:
            composite.pop("qua_dashboards", None)

        return {
            "qualibrate": qualibrate,
            **data,
        }

    @staticmethod
    def forward(data: RawConfigType, config_path: Path) -> RawConfigType:
        data = deepcopy(data)
        new_qualibrate = data.pop("qualibrate")
        version = new_qualibrate.pop("version")
        assert version == Migrate.from_version
        if composite := new_qualibrate.get("composite", None):
            composite.update({"qua_dashboards": {"spawn": True}})
        new_qualibrate["version"] = Migrate.to_version
        new_data = {"qualibrate": new_qualibrate, **data}
        return new_data
