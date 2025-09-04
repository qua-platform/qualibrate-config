import pytest

import qualibrate_config.core.project.switch as switch_module


def test_switch_project_success(mocker, tmp_path):
    project = "alpha"
    config_path = tmp_path / "config.toml"
    config_path.write_text("")

    project_path = tmp_path / "projects" / project
    project_path.mkdir(parents=True)

    patched_get_project_path = mocker.patch(
        "qualibrate_config.core.project.switch.get_project_path",
        return_value=project_path,
    )
    patched_get_config = mocker.patch(
        "qualibrate_config.core.project.switch.get_config_file_content",
        return_value=({"qualibrate": {}}, config_path),
    )
    patched_simple_write = mocker.patch(
        "qualibrate_config.core.project.switch.simple_write"
    )

    result = switch_module.switch_project(config_path, project)

    assert result is True
    patched_get_project_path.assert_called_once_with(tmp_path, project)
    patched_get_config.assert_called_once_with(config_path)
    patched_simple_write.assert_called_once_with(
        config_path, {"qualibrate": {"project": project}}
    )


def test_switch_project_missing_directory_silent(mocker, tmp_path):
    project = "missing_proj"
    config_path = tmp_path / "config.toml"
    project_path = tmp_path / "projects" / project  # does not exist

    patched_get_project_path = mocker.patch(
        "qualibrate_config.core.project.switch.get_project_path",
        return_value=project_path,
    )
    patched_secho = mocker.patch(
        "qualibrate_config.core.project.switch.click.secho"
    )

    result = switch_module.switch_project(config_path, project)

    assert result is False
    patched_get_project_path.assert_called_once_with(tmp_path, project)
    patched_secho.assert_called_once()
    assert (
        f"Can't switch project to '{project}'"
        in patched_secho.call_args.args[0]
    )
    assert project_path.parent.as_posix() in patched_secho.call_args.args[0]


def test_switch_project_missing_directory_raises(mocker, tmp_path):
    project = "bad_proj"
    config_path = tmp_path / "config.toml"
    project_path = tmp_path / "projects" / project  # does not exist

    patched_get_project_path = mocker.patch(
        "qualibrate_config.core.project.switch.get_project_path",
        return_value=project_path,
    )

    with pytest.raises(ValueError) as exc_info:
        switch_module.switch_project(config_path, project, raise_if_error=True)

    patched_get_project_path.assert_called_once_with(tmp_path, project)
    assert f"Can't switch project to '{project}'" in str(exc_info.value)
    assert project_path.parent.as_posix() in str(exc_info.value)
