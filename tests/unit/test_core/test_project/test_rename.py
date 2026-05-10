from pathlib import Path

import pytest

from qualibrate_config.core.project.rename import rename_project


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    path = tmp_path / "qualibrate.toml"
    path.write_text("")
    return path


def test_rename_project_moves_directory_on_disk(config_path: Path) -> None:
    qualibrate_path = config_path.parent

    old_dir = qualibrate_path / "projects" / "old_name"
    old_dir.mkdir(parents=True)
    marker = old_dir / "marker.txt"
    marker.write_text("moved")

    rename_project(config_path, "old_name", "new_name")

    new_dir = qualibrate_path / "projects" / "new_name"
    assert not old_dir.exists()
    assert new_dir.exists()
    assert (new_dir / "marker.txt").read_text() == "moved"


def test_rename_project_old_missing_raises(config_path: Path) -> None:
    with pytest.raises(
        ValueError,
        match="Project 'old_name' does not exist\\.",
    ):
        rename_project(config_path, "old_name", "new_name")


def test_rename_project_new_exists_raises(config_path: Path) -> None:
    qualibrate_path = config_path.parent

    old_dir = qualibrate_path / "projects" / "old_name"
    old_dir.mkdir(parents=True)
    new_dir = qualibrate_path / "projects" / "new_name"
    new_dir.mkdir(parents=True)

    with pytest.raises(
        ValueError, match="Project 'new_name' already exists\\."
    ):
        rename_project(config_path, "old_name", "new_name")


def test_rename_project_failure_is_wrapped(config_path: Path, mocker) -> None:
    qualibrate_path = config_path.parent

    old_dir = qualibrate_path / "projects" / "old_name"
    old_dir.mkdir(parents=True)

    mocker.patch.object(
        Path,
        "rename",
        autospec=True,
        side_effect=OSError("cannot rename"),
    )

    with pytest.raises(
        ValueError,
        match="Project rename failed from 'old_name' to 'new_name'",
    ) as exc_info:
        rename_project(config_path, "old_name", "new_name")

    assert isinstance(exc_info.value.__cause__, OSError)
