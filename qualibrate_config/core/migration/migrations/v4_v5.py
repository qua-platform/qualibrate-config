import shutil
from copy import deepcopy
from pathlib import Path

from qualibrate_config.core.migration.migrations.base import MigrateBase
from qualibrate_config.core.project.create import create_project_config_file
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
        shutil.rmtree("projects", ignore_errors=True)
        return {"qualibrate": qualibrate, **data}

    @staticmethod
    def forward(data: RawConfigType, config_path: Path) -> RawConfigType:
        data = deepcopy(data)
        qualibrate = data.pop("qualibrate")
        assert qualibrate.pop("version") == Migrate.from_version
        qualibrate["version"] = Migrate.to_version
        project_name = qualibrate.get("project")
        new_config = {"qualibrate": qualibrate, **data}
        if project_name is None:
            return new_config
        create_project_config_file(config_path.parent, project_name)
        return new_config
