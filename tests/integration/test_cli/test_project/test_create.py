import sys

from qualibrate_config.models import QualibrateConfig
from qualibrate_config.vars import (
    QUALIBRATE_CONFIG_KEY,
    QUAM_CONFIG_KEY,
    QUAM_STATE_PATH_CONFIG_KEY,
)

if sys.version_info[:2] < (3, 11):
    import tomli as tomllib  # type: ignore[unused-ignore,import-not-found]
else:
    import tomllib

import tomli_w
from click.testing import CliRunner

from qualibrate_config.cli.project.commands.create import create_command
from qualibrate_config.core.project.p_list import list_projects


def test_full_project_creation_pipeline(tmp_path):
    runner = CliRunner()
    config_path = tmp_path / "config.toml"
    projects_path = tmp_path / "projects"
    projects_path.mkdir()
    storage_location = tmp_path / "storage"
    calibration_folder = tmp_path / "calibration"
    quam_state = tmp_path / "quam"
    old_project_name = "init_project"
    new_project_name = "test_project"
    original_config = {
        QUALIBRATE_CONFIG_KEY: {
            "version": QualibrateConfig.version,
            "project": old_project_name,
            "storage": {
                "location": str(tmp_path / "old_storage"),
                "type": "local_storage",
            },
            "calibration_library": {
                "folder": str(tmp_path / "old_calibration"),
                "resolver": "qualibrate.QualibrationLibrary",
            },
        },
        QUAM_CONFIG_KEY: {QUAM_STATE_PATH_CONFIG_KEY: str(tmp_path / "qstate")},
    }
    # Step 1: create initial dummy config file
    with config_path.open("wb") as f:
        tomli_w.dump(original_config, f)

    # Step 2: call the CLI command
    args = [
        new_project_name,
        "--config-path",
        str(config_path),
        "--storage-location",
        str(storage_location),
        "--calibration-library-folder",
        str(calibration_folder),
        "--quam-state-path",
        str(quam_state),
    ]
    print(f"{args = }")
    result = runner.invoke(create_command, args)
    assert result.exit_code == 0
    assert not result.output.strip().startswith("Config file isn't defined")

    # Step 3: validate that project appears in list
    projects_path = tmp_path / "projects"
    assert (projects_path / new_project_name).exists()
    assert new_project_name in list_projects(tmp_path)

    # Step 4: verify project config content
    project_config_file = projects_path / new_project_name / "config.toml"
    assert project_config_file.exists()

    with config_path.open("rb") as f:
        config_after_create = tomllib.load(f)

    with project_config_file.open("rb") as f:
        project_config = tomllib.load(f)

    assert config_after_create == original_config
    assert "qualibrate" in project_config
    assert project_config["qualibrate"]["storage"]["location"] == str(
        storage_location
    )
    assert project_config["qualibrate"]["calibration_library"]["folder"] == str(
        calibration_folder
    )
    assert project_config["quam"]["state_path"] == str(quam_state)
