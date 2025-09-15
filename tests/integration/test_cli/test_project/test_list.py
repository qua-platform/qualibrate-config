import tomli_w
from click.testing import CliRunner

from qualibrate_config.cli.project.commands.list import list_command
from qualibrate_config.models import QualibrateConfig
from qualibrate_config.vars import QUALIBRATE_CONFIG_KEY


def test_list_command_simple(tmp_path):
    runner = CliRunner()
    config_path = tmp_path / "config.toml"
    projects_dir = tmp_path / "projects"
    (projects_dir / "p1").mkdir(parents=True)
    (projects_dir / "p2").mkdir(parents=True)
    config_path.write_text("[qualibrate]\n")

    result = runner.invoke(list_command, ["--config-path", str(config_path)])
    assert result.exit_code == 0
    assert "p1" in result.output
    assert "p2" in result.output


def test_list_command_verbose(tmp_path, capsys):
    runner = CliRunner()
    config_path = tmp_path / "config.toml"
    projects_dir = tmp_path / "projects"
    (projects_dir / "vproj").mkdir(parents=True)
    original_config = {
        QUALIBRATE_CONFIG_KEY: {
            "version": QualibrateConfig.version,
            "project": "vproj",
        },
    }
    with config_path.open("wb") as f:
        tomli_w.dump(original_config, f)

    result = runner.invoke(
        list_command, ["--config-path", str(config_path), "--verbose"]
    )

    assert result.exit_code == 0
    out = result.output
    assert "Project: vproj" in out
    assert "nodes_number: " in out
    assert "created_at: " in out
    assert "last_modified_at: " in out
    assert "config overrides: " in out
