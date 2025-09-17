import shutil
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from qualibrate_config.core.migration.migrations.base import MigrateBase
from qualibrate_config.core.project.create import create_project_config_file
from qualibrate_config.core.project.path import get_projects_path
from qualibrate_config.qulibrate_types import RawConfigType


class Migrate(MigrateBase):
    from_version: int = 4
    to_version: int = 5

    @staticmethod
    def backward(data: RawConfigType, config_path: Path) -> RawConfigType:
        data = deepcopy(data)
        qualibrate = data.pop("qualibrate")
        assert qualibrate.pop("version") == Migrate.to_version
        qualibrate["version"] = Migrate.from_version
        shutil.rmtree(get_projects_path(config_path.parent), ignore_errors=True)
        return {"qualibrate": qualibrate, **data}

    @staticmethod
    def forward(data: RawConfigType, config_path: Path) -> RawConfigType:
        data = deepcopy(data)
        qualibrate = data.pop("qualibrate")
        assert qualibrate.pop("version") == Migrate.from_version
        qualibrate["version"] = Migrate.to_version
        if (runner := qualibrate.get("runner")) and (
            address := runner.get("address")
        ):
            parsed = urlparse(address)
            if parsed.hostname == "localhost":
                runner["address"] = urlunparse(
                    parsed._replace(
                        netloc=parsed.netloc.replace("localhost", "127.0.0.1")
                    )
                )
        project_name = qualibrate.get("project")
        new_config = {"qualibrate": qualibrate, **data}
        if project_name is None:
            return new_config
        create_project_config_file(config_path.parent, project_name)
        return new_config
