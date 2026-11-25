import sys
from pathlib import Path

import pytest

if sys.version_info[:2] < (3, 11):
    import tomli as tomllib  # type: ignore[unused-ignore,import-not-found]
else:
    import tomllib

from qualibrate_config.core.project.path import get_project_config_path
from qualibrate_config.core.project.update import update_project
from qualibrate_config.models import DatabaseStateConfig, DBConfig

PROJECT_NAME = "probe"


@pytest.fixture
def qualibrate_path(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def global_storage(qualibrate_path: Path) -> Path:
    return qualibrate_path / "global_storage"


@pytest.fixture
def config_path(qualibrate_path: Path, global_storage: Path) -> Path:
    path = qualibrate_path / "config.toml"
    path.write_text(f'[qualibrate.storage]\nlocation = "{global_storage}"\n')
    return path


@pytest.fixture
def project_storage(qualibrate_path: Path) -> Path:
    return qualibrate_path / "probe_storage"


@pytest.fixture
def quam_state_path(qualibrate_path: Path) -> Path:
    return qualibrate_path / "probe_state"


@pytest.fixture
def project_config_file(
    qualibrate_path: Path, project_storage: Path, quam_state_path: Path
) -> Path:
    path = get_project_config_path(qualibrate_path, PROJECT_NAME)
    path.parent.mkdir(parents=True)
    path.write_text(
        f'[quam]\nstate_path = "{quam_state_path}"\n\n'
        f'[qualibrate.storage]\nlocation = "{project_storage}"\n'
    )
    return path


def _read(path: Path) -> dict:
    return tomllib.loads(path.read_text())


def test_database_only_update_keeps_project_overrides(
    config_path: Path,
    project_config_file: Path,
    project_storage: Path,
    quam_state_path: Path,
) -> None:
    update_project(
        config_path,
        PROJECT_NAME,
        database=DBConfig({"host": "db-host", "port": 5432, "database": "qm"}),
        database_state=DatabaseStateConfig({"is_connected": False}),
    )

    data = _read(project_config_file)
    assert data["quam"]["state_path"] == str(quam_state_path)
    assert data["qualibrate"]["storage"]["location"] == str(project_storage)
    assert data["qualibrate"]["database"]["host"] == "db-host"


def test_storage_update_keeps_state_path(
    config_path: Path,
    project_config_file: Path,
    quam_state_path: Path,
    qualibrate_path: Path,
) -> None:
    new_storage = qualibrate_path / "new_storage"

    update_project(config_path, PROJECT_NAME, storage_location=new_storage)

    data = _read(project_config_file)
    assert data["quam"]["state_path"] == str(quam_state_path)
    assert data["qualibrate"]["storage"]["location"] == str(new_storage)


def test_explicit_value_equal_to_global_overrides_project(
    config_path: Path,
    project_config_file: Path,
    global_storage: Path,
) -> None:
    update_project(config_path, PROJECT_NAME, storage_location=global_storage)

    data = _read(project_config_file)
    assert data["qualibrate"]["storage"]["location"] == str(global_storage)


def test_update_does_not_copy_global_config_into_project(
    config_path: Path,
    qualibrate_path: Path,
) -> None:
    project_config_file = get_project_config_path(qualibrate_path, PROJECT_NAME)
    project_config_file.parent.mkdir(parents=True)
    project_config_file.write_text("")

    update_project(
        config_path,
        PROJECT_NAME,
        database_state=DatabaseStateConfig({"is_connected": False}),
    )

    data = _read(project_config_file)
    assert "storage" not in data.get("qualibrate", {})


def test_update_missing_project_raises(config_path: Path) -> None:
    with pytest.raises(ValueError, match="Project 'probe' does not exist\\."):
        update_project(config_path, PROJECT_NAME, storage_location=None)
