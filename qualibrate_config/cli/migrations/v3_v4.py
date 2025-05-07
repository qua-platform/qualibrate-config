from importlib.util import find_spec
from pathlib import Path
from typing import Optional

from qualibrate_config.cli.migrations.base import MigrateBase
from qualibrate_config.qulibrate_types import RawConfigType


class Migrate(MigrateBase):
    from_version: int = 3
    to_version: int = 4

    @staticmethod
    def backward(data: RawConfigType) -> RawConfigType:
        qualibrate = data.pop("qualibrate")
        assert qualibrate.pop("version") == Migrate.to_version
        qualibrate["version"] = Migrate.from_version
        app: Optional[RawConfigType] = qualibrate.get("app", None)
        if app is None:
            return {"qualibrate": qualibrate, **data}
        static_files = app.get("static_site_files")
        if static_files is not None:
            return {"qualibrate": qualibrate, **data}
        app_module = find_spec("qualibrate_app")
        if app_module is None or app_module.origin is None:
            return {"qualibrate": qualibrate, **data}
        module_path = Path(app_module.origin)
        app["static_site_files"] = str(
            module_path.parents[1] / "qualibrate_static"
        )
        return {"qualibrate": qualibrate, **data}

    @staticmethod
    def forward(data: RawConfigType) -> RawConfigType:
        new_qualibrate = data.pop("qualibrate")
        version = new_qualibrate.pop("version")
        assert version == Migrate.from_version
        new_qualibrate["version"] = Migrate.to_version
        app: Optional[RawConfigType] = new_qualibrate.get("app", None)

        if app is None:
            return {"qualibrate": new_qualibrate, **data}
        static_files = app.get("static_site_files")
        if static_files is None:
            return {"qualibrate": new_qualibrate, **data}
        path = Path(static_files)
        if tuple(path.parts[-2:]) == ("site-packages", "qualibrate_static"):
            app.pop("static_site_files", None)
        return {"qualibrate": new_qualibrate, **data}
