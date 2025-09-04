import qualibrate_config.core.project.path as path_m
from qualibrate_config.vars import DEFAULT_CONFIG_FILENAME


def test_get_projects_path_returns_correct_path(tmp_path):
    result = path_m.get_projects_path(tmp_path)
    assert result == tmp_path / "projects"


def test_get_project_path_returns_nested_path(tmp_path):
    result = path_m.get_project_path(tmp_path, "example_project")
    assert result == tmp_path / "projects" / "example_project"


def test_get_project_config_path_with_default_filename(tmp_path):
    result = path_m.get_project_config_path(tmp_path, "my_proj")
    expected = tmp_path / "projects" / "my_proj" / DEFAULT_CONFIG_FILENAME
    assert result == expected


def test_get_project_config_path_with_custom_filename(tmp_path):
    result = path_m.get_project_config_path(tmp_path, "my_proj", "custom.toml")
    expected = tmp_path / "projects" / "my_proj" / "custom.toml"
    assert result == expected
