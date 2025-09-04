import sys

import tomli_w
from click.testing import CliRunner

from qualibrate_config.cli.project.commands.switch import switch_command
from qualibrate_config.models import QualibrateConfig
from qualibrate_config.vars import QUALIBRATE_CONFIG_KEY

if sys.version_info[:2] < (3, 11):
    import tomli as tomllib  # type: ignore[unused-ignore,import-not-found]
else:
    import tomllib


def test_switch_command_success(tmp_path):
    runner = CliRunner()
    config_path = tmp_path / "config.toml"
    project_name = "my_project"
    original_config = {
        QUALIBRATE_CONFIG_KEY: {
            "version": QualibrateConfig.version,
            "project": "current",
        },
    }
    with config_path.open("wb") as f:
        tomli_w.dump(original_config, f)
    project_dir = tmp_path / "projects" / project_name
    project_dir.mkdir(parents=True)

    result = runner.invoke(
        switch_command,
        [project_name, "--config-path", str(config_path)],
    )

    assert result.exit_code == 0
    assert f"Project switched to '{project_name}'." in result.output
    with config_path.open("rb") as f:
        new_config = tomllib.load(f)

    assert new_config[QUALIBRATE_CONFIG_KEY]["project"] == project_name


def test_switch_command_failure_nonexistent_project(tmp_path):
    runner = CliRunner()
    config_path = tmp_path / "config.toml"
    config_path.touch()

    result = runner.invoke(
        switch_command,
        ["does_not_exist", "--config-path", str(config_path)],
    )

    assert result.exit_code == 1
    assert "Can't switch project to 'does_not_exist'" in result.output
