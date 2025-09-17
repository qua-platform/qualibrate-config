from pathlib import Path

import tomli_w
from click.testing import CliRunner

from qualibrate_config.cli.project.commands.delete import delete_command


def write_toml(path: Path, data: dict) -> None:
    with path.open("wb") as f:
        tomli_w.dump(data, f)


def test_delete_command_success(tmp_path):
    runner = CliRunner()
    project_name = "project1"
    project_path = tmp_path / "projects" / project_name
    storage_path = project_path / "storage"
    quam_path = project_path / "quam"
    config_path = tmp_path / "config.toml"

    # Create directories
    storage_path.mkdir(parents=True)
    quam_path.mkdir(parents=True)

    # Write config
    config = {
        "qualibrate": {
            "project": "other_project",
            "storage": {"location": str(storage_path)},
        },
        "quam": {"state_path": str(quam_path)},
    }
    write_toml(config_path, config)

    result = runner.invoke(
        delete_command,
        [project_name, "--config-path", str(config_path)],
    )

    assert result.exit_code == 0
    assert f"Successfully removed project '{project_name}'" in result.output
    assert not project_path.exists()
    assert not storage_path.exists()
    assert not quam_path.exists()


def test_delete_command_fails_for_current_project(tmp_path):
    runner = CliRunner()
    project_name = "active_project"
    project_path = tmp_path / "projects" / project_name
    project_path.mkdir(parents=True)
    config_path = tmp_path / "config.toml"

    config = {"qualibrate": {"project": project_name}}
    write_toml(config_path, config)

    result = runner.invoke(
        delete_command,
        [project_name, "--config-path", str(config_path)],
    )

    assert result.exit_code == 1
    assert f"Failed to remove project '{project_name}'" in result.output
    assert "Can't delete current project" in result.output
    assert project_path.exists()


def test_delete_command_does_not_remove_external_dirs(tmp_path):
    runner = CliRunner()
    project_name = "external_case"
    project_path = tmp_path / "projects" / project_name
    storage_path = tmp_path / "external_storage"
    quam_path = tmp_path / "external_quam"
    config_path = tmp_path / "config.toml"

    # Create directories
    project_path.mkdir(parents=True)
    storage_path.mkdir()
    quam_path.mkdir()

    config = {
        "qualibrate": {
            "project": "other_project",
            "storage": {"location": str(storage_path)},
        },
        "quam": {"state_path": str(quam_path)},
    }
    write_toml(config_path, config)

    result = runner.invoke(
        delete_command,
        [project_name, "--config-path", str(config_path)],
    )

    assert result.exit_code == 0
    assert f"Successfully removed project '{project_name}'" in result.output
    assert not project_path.exists()
    assert storage_path.exists()
    assert quam_path.exists()
