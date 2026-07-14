from copy import deepcopy
from pathlib import Path

from qualibrate_config.core.migration.migrations.base import MigrateBase
from qualibrate_config.qulibrate_types import RawConfigType


class Migrate(MigrateBase):
    """Copy `app.static_site_files` to `composite.static_site_files`."""

    from_version: int = 5
    to_version: int = 6

    @staticmethod
    def backward(data: RawConfigType, config_path: Path) -> RawConfigType:
        data = deepcopy(data)
        qualibrate = data.pop("qualibrate")
        assert qualibrate.pop("version") == Migrate.to_version
        qualibrate["version"] = Migrate.from_version
        composite = qualibrate.get("composite")
        if composite is not None:
            composite.pop("static_site_files", None)
        return {"qualibrate": qualibrate, **data}

    @staticmethod
    def forward(data: RawConfigType, config_path: Path) -> RawConfigType:
        data = deepcopy(data)
        qualibrate = data.pop("qualibrate")
        assert qualibrate.pop("version") == Migrate.from_version
        qualibrate["version"] = Migrate.to_version
        app: RawConfigType | None = qualibrate.get("app")
        static_files = app.get("static_site_files") if app is not None else None
        if static_files is not None:
            composite = qualibrate.setdefault("composite", {})
            composite.setdefault("static_site_files", static_files)
        return {"qualibrate": qualibrate, **data}
