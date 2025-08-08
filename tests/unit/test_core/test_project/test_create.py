import sys

import pytest

if sys.version_info[:2] < (3, 11):
    import tomli as tomllib  # type: ignore[unused-ignore,import-not-found]
else:
    import tomllib

from pathlib import Path
from types import SimpleNamespace

import click
import jsonpatch
from pydantic import BaseModel, computed_field

from qualibrate_config.core.project import create as create_m
from qualibrate_config.models import PathSerializer
from qualibrate_config.vars import (
    QUALIBRATE_CONFIG_KEY,
    QUAM_CONFIG_KEY,
    QUAM_STATE_PATH_CONFIG_KEY,
)


class Paths(BaseModel):
    qualibrate_path: Path

    @computed_field
    def config_path(self) -> Path:
        return self.qualibrate_path / "config.toml"

    @computed_field
    def projects_path(self) -> Path:
        return self.qualibrate_path / "projects"

    @computed_field
    def storage_location(self) -> Path:
        return self.qualibrate_path / "storage"

    @computed_field
    def calibration_library_folder(self) -> Path:
        return self.qualibrate_path / "calibrations"

    @computed_field
    def quam_state_path(self) -> Path:
        return self.qualibrate_path / "quam_state_path"


@pytest.fixture
def paths(tmp_path) -> Paths:
    return Paths(qualibrate_path=tmp_path)


def test__fill_path_sets_value():
    config = {}
    path = ["a", "b"]
    key = "test"
    value = Path("/my/test/path")
    create_m._fill_path(config, path, key, value)
    assert config["a"]["b"]["test"] == PathSerializer.serialize_path(value)


def test__fill_path_skips_none():
    config = {"a": {"b": {}}}
    create_m._fill_path(config, ["a", "b"], "key", None)
    assert config["a"]["b"] == {}


def test_fill_project_storage_location_sets_path(mocker):
    cfg = {}
    patched = mocker.patch("qualibrate_config.core.project.create._fill_path")
    loc = Path("/tmp/storage")
    create_m.fill_project_storage_location(cfg, loc)
    patched.assert_called_once_with(
        cfg,
        [QUALIBRATE_CONFIG_KEY, "storage"],
        "location",
        loc,
    )


def test_fill_project_calibration_library_folder_sets_path(mocker):
    cfg = {}
    patched = mocker.patch("qualibrate_config.core.project.create._fill_path")
    loc = Path("/tmp/calibration")
    create_m.fill_project_calibration_library_folder(cfg, loc)
    patched.assert_called_once_with(
        cfg,
        [QUALIBRATE_CONFIG_KEY, "calibration_library"],
        "folder",
        loc,
    )


def test_fill_project_quam_state_path_sets_path():
    cfg = {}
    create_m.fill_project_quam_state_path(cfg, Path("/tmp/quam"))
    assert cfg[QUAM_CONFIG_KEY][
        QUAM_STATE_PATH_CONFIG_KEY
    ] == PathSerializer.serialize_path(Path("/tmp/quam"))


def test_after_create_project_creates_dirs(paths: Paths):
    create_m.after_create_project(paths.storage_location, paths.quam_state_path)
    assert paths.storage_location.exists()
    assert paths.quam_state_path.exists()


def test_create_project_config_file_with_config(paths: Paths):
    project_name = "myproj"
    config_overrides = {"a": 1}
    create_m.create_project_config_file(
        paths.qualibrate_path, project_name, config_overrides
    )
    p = paths.projects_path / project_name / "config.toml"
    assert p.exists()
    assert tomllib.loads(p.read_text()) == {"a": 1}


def test_create_project_config_file_empty(paths: Paths):
    project_name = "empty"
    create_m.create_project_config_file(paths.qualibrate_path, project_name)
    p = paths.projects_path / project_name / "config.toml"
    assert p.exists()
    assert tomllib.loads(p.read_text()) == {}


def test_rollback_project_creation_removes_all(paths: Paths):
    paths.qualibrate_path.mkdir(exist_ok=True)
    project_path = paths.projects_path / "project"
    project_path.mkdir(parents=True)
    paths.storage_location.mkdir()
    paths.quam_state_path.mkdir()
    create_m.rollback_project_creation(
        paths.qualibrate_path,
        "project",
        paths.storage_location,
        paths.quam_state_path,
    )
    assert not project_path.exists()
    assert not paths.storage_location.exists()
    assert not paths.quam_state_path.exists()


def test_config_for_project_from_context_valid(mocker, paths):
    cfg = {}
    dummy_command = click.Command("dummy")
    context = click.Context(dummy_command)

    qualibrate_config_from_sources = mocker.patch(
        "qualibrate_config.core.project.create.qualibrate_config_from_sources",
        return_value={
            "storage": {"location": "foo"},
            "calibration_library": {"resolver": "r"},
        },
    )
    mocker.patch(
        "qualibrate_config.core.project.create.QualibrateTopLevelConfig",
        side_effect=lambda d: SimpleNamespace(serialize=lambda: d),
    )

    result = create_m.config_for_project_from_context(
        cfg,
        paths.storage_location,
        paths.calibration_library_folder,
        paths.quam_state_path,
        context,
    )

    assert QUALIBRATE_CONFIG_KEY in result
    assert QUAM_CONFIG_KEY in result
    qualibrate_config_from_sources.assert_called_once()


def test_config_for_project_from_context_calibration_library_without_resolver(
    mocker, paths
):
    cfg = {}
    dummy_command = click.Command("dummy")
    context = click.Context(dummy_command)

    mocker.patch(
        "qualibrate_config.core.project.create.qualibrate_config_from_sources",
        return_value={"storage": {"location": "foo"}},
    )
    mocker.patch(
        "qualibrate_config.core.project.create.QualibrateTopLevelConfig",
        side_effect=lambda d: SimpleNamespace(serialize=lambda: d),
    )
    with pytest.raises(ValueError):
        create_m.config_for_project_from_context(
            cfg,
            paths.storage_location,
            paths.calibration_library_folder,
            paths.quam_state_path,
            context,
        )



def test_config_for_project_from_context_raises_if_none():
    with pytest.raises(ValueError):
        create_m.config_for_project_from_context({}, None, None, None, None)


def test_config_for_project_from_args_sets_all(paths: Paths):
    cfg = {}
    result = create_m.config_for_project_from_args(
        cfg,
        paths.storage_location,
        paths.calibration_library_folder,
        paths.quam_state_path,
        None,
    )
    assert QUALIBRATE_CONFIG_KEY in result
    assert QUAM_CONFIG_KEY in result


def test_config_for_project_from_args_raises_on_ctx():
    with pytest.raises(ValueError):
        create_m.config_for_project_from_args({}, None, None, None, "ctx")


def test_jsonpatch_to_dict_nested_fields():
    patch = jsonpatch.JsonPatch(
        [
            {"op": "replace", "path": "/foo/bar", "value": 1},
            {"op": "replace", "path": "/foo/baz", "value": 2},
        ]
    )
    d = create_m.jsonpatch_to_dict(patch)
    assert d["foo"]["bar"] == 1
    assert d["foo"]["baz"] == 2


@pytest.mark.parametrize("ctx", [None, "ctx"])
def test_create_project_success(mocker, paths, ctx):
    paths.config_path.write_text("dummy")
    old_config = {"some": "config"}
    new_config = {"some": "new config"}
    list_projects_patched = mocker.patch(
        "qualibrate_config.core.project.create.list_projects", return_value=[]
    )
    file_content_patched = mocker.patch(
        "qualibrate_config.core.project.create.get_config_file_content",
        return_value=(old_config, paths.config_path),
    )
    migrate_patched = mocker.patch(
        (
            "qualibrate_config.core.project.create"
            ".validate_version_and_migrate_if_needed"
        ),
        return_value=(old_config, paths.config_path),
    )
    patched_create_from_args = mocker.patch(
        "qualibrate_config.core.project.create.config_for_project_from_args",
        return_value=new_config,
    )
    patched_create_from_ctx = mocker.patch(
        "qualibrate_config.core.project.create.config_for_project_from_context",
        return_value=new_config,
    )
    patched_jsonpatch_to_dict = mocker.patch(
        "qualibrate_config.core.project.create.jsonpatch_to_dict",
        return_value=new_config,
    )
    patched_create_pcf = mocker.patch(
        "qualibrate_config.core.project.create.create_project_config_file"
    )
    patched_after_create = mocker.patch(
        "qualibrate_config.core.project.create.after_create_project"
    )

    create_m.create_project(
        paths.config_path,
        "proj",
        paths.storage_location,
        None,
        paths.quam_state_path,
        ctx=ctx,
    )

    list_projects_patched.assert_called_once_with(paths.qualibrate_path)
    file_content_patched.assert_called_once_with(paths.config_path)
    migrate_patched.assert_called_once_with(old_config, paths.config_path)
    patched_create_c, patched_create_nc = (
        (patched_create_from_args, patched_create_from_ctx)
        if ctx is None
        else (patched_create_from_ctx, patched_create_from_args)
    )
    patched_create_c.assert_called_once_with(
        old_config,
        paths.storage_location,
        None,
        paths.quam_state_path,
        ctx,
    )
    patched_create_nc.assert_not_called()
    patched_jsonpatch_to_dict.assert_called_once()
    assert (
        patched_jsonpatch_to_dict.call_args[0][0].to_string()
        == '[{"op": "replace", "path": "/some", "value": "new config"}]'
    )
    patched_create_pcf.assert_called_once_with(
        paths.qualibrate_path, "proj", new_config
    )
    patched_after_create.assert_called_once_with(
        paths.storage_location, paths.quam_state_path
    )


def test_create_project_exists(mocker, paths):
    mocker.patch(
        "qualibrate_config.core.project.create.list_projects",
        return_value=["proj"],
    )
    with pytest.raises(ValueError):
        create_m.create_project(paths.config_path, "proj", None, None, None)


def test_create_project_fails_and_rolls_back(mocker, tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text("dummy")
    mocker.patch(
        "qualibrate_config.core.project.create.list_projects", return_value=[]
    )
    mocker.patch(
        "qualibrate_config.core.project.create.get_config_file_content",
        return_value=({}, config_path),
    )
    mocker.patch(
        "qualibrate_config.core.project.create.validate_version_and_migrate_if_needed",
        return_value=({}, config_path),
    )
    mocker.patch(
        "qualibrate_config.core.project.create.config_for_project_from_args",
        return_value={"some": "config"},
    )
    mocker.patch(
        "qualibrate_config.core.project.create.jsonpatch_to_dict",
        return_value={},
    )
    mocker.patch(
        "qualibrate_config.core.project.create.create_project_config_file",
        side_effect=OSError("fail"),
    )
    rollback_mock = mocker.patch(
        "qualibrate_config.core.project.create.rollback_project_creation"
    )

    with pytest.raises(ValueError, match="Project creation failed. fail"):
        create_m.create_project(config_path, "proj", None, None, None)

    rollback_mock.assert_called_once()
