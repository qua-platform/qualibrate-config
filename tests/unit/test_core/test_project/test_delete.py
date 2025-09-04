import pytest

import qualibrate_config.core.project.delete as delete_module


def test_delete_project_success(mocker, tmp_path):
    config_path = tmp_path / "config.toml"
    project_name = "to_delete"
    project_path = tmp_path / "projects" / project_name
    project_path.mkdir(parents=True)

    patched_list_projects = mocker.patch(
        "qualibrate_config.core.project.delete.list_projects",
        return_value=[project_name],
    )
    patched_get_config = mocker.patch(
        "qualibrate_config.core.project.delete.get_config_file_content",
        return_value=({}, config_path),
    )
    patched_get_current_project = mocker.patch(
        "qualibrate_config.core.project.delete.get_project_from_common_config",
        return_value=None,
    )
    patched_get_project_path = mocker.patch(
        "qualibrate_config.core.project.delete.get_project_path",
        return_value=project_path,
    )
    patched_rmtree = mocker.patch(
        "qualibrate_config.core.project.delete.shutil.rmtree"
    )

    delete_module.delete_project(config_path, project_name)

    patched_list_projects.assert_called_once_with(tmp_path)
    patched_get_config.assert_called_once_with(config_path)
    patched_get_current_project.assert_called_once_with({})
    patched_get_project_path.assert_called_once_with(tmp_path, project_name)
    patched_rmtree.assert_called_once_with(project_path)


def test_delete_project_does_not_exist(mocker, tmp_path):
    config_path = tmp_path / "config.toml"
    mocker.patch(
        "qualibrate_config.core.project.delete.list_projects",
        return_value=["proj1", "proj2"],
    )
    with pytest.raises(RuntimeError, match="does not exist"):
        delete_module.delete_project(config_path, "missing_project")


def test_delete_project_currently_active(mocker, tmp_path):
    config_path = tmp_path / "config.toml"
    project = "active_project"

    mocker.patch(
        "qualibrate_config.core.project.delete.list_projects",
        return_value=[project],
    )
    mocker.patch(
        "qualibrate_config.core.project.delete.get_config_file_content",
        return_value=({}, config_path),
    )
    mocker.patch(
        "qualibrate_config.core.project.delete.get_project_from_common_config",
        return_value=project,
    )

    with pytest.raises(RuntimeError, match="Can't delete current project"):
        delete_module.delete_project(config_path, project)


def test_delete_project_path_is_none(mocker, tmp_path):
    config_path = tmp_path / "config.toml"
    project = "orphan_project"

    mocker.patch(
        "qualibrate_config.core.project.delete.list_projects",
        return_value=[project],
    )
    mocker.patch(
        "qualibrate_config.core.project.delete.get_config_file_content",
        return_value=({}, config_path),
    )
    mocker.patch(
        "qualibrate_config.core.project.delete.get_project_from_common_config",
        return_value=None,
    )
    mocker.patch(
        "qualibrate_config.core.project.delete.get_project_path",
        return_value=None,
    )

    with pytest.raises(RuntimeError, match="Can't resolve project"):
        delete_module.delete_project(config_path, project)
