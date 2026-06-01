import sys
from copy import deepcopy
from pathlib import Path

from qualibrate_config.core.migration.migrations.base import MigrateBase
from qualibrate_config.qulibrate_types import RawConfigType


class Migrate(MigrateBase):
    from_version: int = 3
    to_version: int = 4

    @staticmethod
    def backward(data: RawConfigType, config_path: Path) -> RawConfigType:
        data = deepcopy(data)
        qualibrate = data.pop("qualibrate")
        assert qualibrate.pop("version") == Migrate.to_version
        qualibrate["version"] = Migrate.from_version
        app: RawConfigType | None = qualibrate.get("app", None)
        if app is None:
            return {"qualibrate": qualibrate, **data}
        static_files = app.get("static_site_files")
        if static_files is not None:
            return {"qualibrate": qualibrate, **data}
        # Walk sys.path to find qualibrate_app's install location. Nuitka-safe
        # alternative to find_spec("qualibrate_app").origin (which returns a
        # phantom path under obfuscated builds). Semantics preserved: find the
        # qualibrate_app package dir, go up one level (to site-packages), and
        # append "qualibrate_static".
        for entry in sys.path:
            qa_dir = Path(entry) / "qualibrate_app"
            if qa_dir.is_dir():
                app["static_site_files"] = str(
                    qa_dir.parent / "qualibrate_static"
                )
                break
        return {"qualibrate": qualibrate, **data}

    @staticmethod
    def forward(data: RawConfigType, config_path: Path) -> RawConfigType:
        data = deepcopy(data)
        new_qualibrate = data.pop("qualibrate")
        version = new_qualibrate.pop("version")
        assert version == Migrate.from_version
        new_qualibrate["version"] = Migrate.to_version
        app: RawConfigType | None = new_qualibrate.get("app", None)

        if app is None:
            return {"qualibrate": new_qualibrate, **data}
        static_files = app.get("static_site_files")
        if static_files is None:
            return {"qualibrate": new_qualibrate, **data}
        path = Path(static_files)
        if tuple(path.parts[-2:]) == ("site-packages", "qualibrate_static"):
            app.pop("static_site_files", None)
        return {"qualibrate": new_qualibrate, **data}
