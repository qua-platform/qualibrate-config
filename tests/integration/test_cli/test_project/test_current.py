import tomli_w
from click.testing import CliRunner

from qualibrate_config.cli.project.commands.current import current_command
from qualibrate_config.models import QualibrateConfig
from qualibrate_config.vars import QUALIBRATE_CONFIG_KEY


def test_current_command_with_project_set(tmp_path):
    runner = CliRunner()
    config_path = tmp_path / "config.toml"
    project_name = "example_project"
    project_dir = tmp_path / "projects" / project_name
    project_dir.mkdir(parents=True)
    (project_dir / "config.toml").touch()
    original_config = {
        QUALIBRATE_CONFIG_KEY: {
            "version": QualibrateConfig.version,
            "project": project_name,
        },
    }
    with config_path.open("wb") as f:
        tomli_w.dump(original_config, f)

    result = runner.invoke(current_command, ["--config-path", str(config_path)])

    assert result.exit_code == 0
    assert f"Current project is {project_name}" in result.output


def test_current_command_without_project_dir(tmp_path):
    runner = CliRunner()
    config_path = tmp_path / "config.toml"
    project_name = "example_project"
    original_config = {
        QUALIBRATE_CONFIG_KEY: {
            "version": QualibrateConfig.version,
            "project": project_name,
        },
    }
    with config_path.open("wb") as f:
        tomli_w.dump(original_config, f)

    # Simulate config with no project entry

    result = runner.invoke(current_command, ["--config-path", str(config_path)])

    assert result.exit_code == 1
    assert "Can't resolve currently active project" in result.output


def test_current_command_without_project_set(tmp_path):
    runner = CliRunner()
    config_path = tmp_path / "config.toml"
    config_path.touch()
    # Simulate config with no project entry

    result = runner.invoke(current_command, ["--config-path", str(config_path)])

    assert result.exit_code == 1
    assert "Can't resolve currently active project" in result.output
