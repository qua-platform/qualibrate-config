import tomli_w

from qualibrate_config.core.project import common as common_m
from qualibrate_config.vars import QUALIBRATE_CONFIG_KEY


def test_get_project_from_common_config_returns_project():
    config = {QUALIBRATE_CONFIG_KEY: {"project": "my_project"}}
    result = common_m.get_project_from_common_config(config)
    assert result == "my_project"


def test_get_project_from_common_config_missing_key():
    config = {}  # No 'qualibrate' key
    result = common_m.get_project_from_common_config(config)
    assert result is None


def test_read_project_config_file_exists(mocker, tmp_path):
    config_file = tmp_path / "config.toml"
    project_name = "test_project"
    project_dir = tmp_path / project_name
    project_dir.mkdir()
    p_config_file = project_dir / "project_config.toml"
    with open(p_config_file, "wb") as f:
        tomli_w.dump({QUALIBRATE_CONFIG_KEY: {"project": project_name}}, f)

    patched_project_cp = mocker.patch(
        "qualibrate_config.core.project.common.get_project_config_path",
        return_value=p_config_file,
    )

    result = common_m.read_project_config_file(config_file, project_name)
    assert QUALIBRATE_CONFIG_KEY in result
    patched_project_cp.assert_called_once_with(tmp_path, project_name)


def test_read_project_config_file_missing(mocker, tmp_path):
    config_file = tmp_path / "config.toml"
    project_name = "missing_project"
    p_config_file = tmp_path / project_name / "project_config.toml"
    mocker.patch(
        "qualibrate_config.core.project.common.get_project_config_path",
        return_value=p_config_file,
    )
    result = common_m.read_project_config_file(config_file, project_name)
    assert result == {}
