from datetime import datetime
from os import stat_result

import pytest

import qualibrate_config.core.project.p_list as p_list


def test_dt_from_ts_conversion():
    ts = 1754298000
    dt = p_list._dt_from_ts(ts)
    assert isinstance(dt, datetime)
    assert dt.timestamp() == round(ts)


def test_created_at_from_storage_no_dirs(mocker, tmp_path):
    mtime_ts = 1754298000
    storage_stat = stat_result(
        [16832, -1, -1, 2, 1000, 1000, 4096, 1754377837, mtime_ts, 1754299000]
    )
    dt = datetime.fromtimestamp(mtime_ts)
    patched_dt_from_ts = mocker.patch(
        "qualibrate_config.core.project.p_list._dt_from_ts", return_value=dt
    )
    patched_stat_ctime = mocker.patch(
        "qualibrate_config.core.project.p_list._stat_ctime"
    )
    patched_file_stat_ctime = mocker.patch(
        "qualibrate_config.core.project.p_list._file_stat_ctime"
    )
    assert p_list._created_at_from_storage(tmp_path, storage_stat) == dt
    patched_stat_ctime.assert_called_once_with(storage_stat)
    patched_dt_from_ts.assert_called_once()
    patched_file_stat_ctime.assert_not_called()


@pytest.mark.parametrize(
    "storage_ts, subdir_ts, expected",
    (
        (1754299000, 1754298000, 1754298000),
        (1754298000, 1754299000, 1754298000),
    ),
)
def test_created_at_from_storage_with_dirs_subdir_ctime(
    mocker, tmp_path, storage_ts, subdir_ts, expected
):
    subdir = tmp_path / "a" / "#node"
    storage_ts = storage_ts
    subdir_ts = subdir_ts
    storage_stat = stat_result(
        [16832, -1, -1, 2, 1000, 1000, 4096, 1754377837, 1754377837, storage_ts]
    )
    dt = datetime.fromtimestamp(subdir_ts)
    subdir.mkdir(parents=True)
    patched_file_stat_ctime = mocker.patch(
        "qualibrate_config.core.project.p_list._file_stat_ctime",
        return_value=subdir_ts,
    )
    patched_stat_ctime = mocker.patch(
        "qualibrate_config.core.project.p_list._stat_ctime",
        return_value=storage_ts,
    )
    patched_dt_from_ts = mocker.patch(
        "qualibrate_config.core.project.p_list._dt_from_ts", return_value=dt
    )
    result = p_list._created_at_from_storage(tmp_path, storage_stat)
    assert isinstance(result, datetime)
    assert patched_file_stat_ctime.call_count == 2
    patched_file_stat_ctime.assert_has_calls(
        [mocker.call(subdir), mocker.call(subdir)]
    )
    patched_stat_ctime.assert_called_once_with(storage_stat)
    patched_dt_from_ts.assert_called_once_with(expected)


def test_last_modified_at_from_storage_no_dirs(mocker, tmp_path):
    mtime_ts = 1754298000
    storage_stat = stat_result(
        [16832, -1, -1, 2, 1000, 1000, 4096, 1754377837, mtime_ts, 1754299000]
    )
    dt = datetime.fromtimestamp(mtime_ts)
    patched_dt_from_ts = mocker.patch(
        "qualibrate_config.core.project.p_list._dt_from_ts", return_value=dt
    )
    patched_file_stat_mtime = mocker.patch(
        "qualibrate_config.core.project.p_list._file_stat_mtime"
    )
    assert p_list._last_modified_at_from_storage(tmp_path, storage_stat) == dt
    patched_dt_from_ts.assert_called_once_with(mtime_ts)
    patched_file_stat_mtime.assert_not_called()


@pytest.mark.parametrize(
    "storage_ts, subdir_ts, expected",
    (
        (1754300000, 1754301000, 1754301000),
        (1754302000, 1754301000, 1754302000),
    ),
)
def test_last_modified_at_from_storage_with_dirs(
    mocker, tmp_path, storage_ts, subdir_ts, expected
):
    subdir = tmp_path / "a" / "#node"
    subdir.mkdir(parents=True)

    storage_stat = stat_result(
        [16832, -1, -1, 2, 1000, 1000, 4096, 1754377837, storage_ts, 1754377837]
    )
    dt = datetime.fromtimestamp(expected)

    patched_file_stat_mtime = mocker.patch(
        "qualibrate_config.core.project.p_list._file_stat_mtime",
        return_value=subdir_ts,
    )
    patched_dt_from_ts = mocker.patch(
        "qualibrate_config.core.project.p_list._dt_from_ts", return_value=dt
    )

    result = p_list._last_modified_at_from_storage(tmp_path, storage_stat)
    assert isinstance(result, datetime)
    assert result == dt
    assert patched_file_stat_mtime.call_count == 2
    patched_file_stat_mtime.assert_has_calls(
        [mocker.call(subdir), mocker.call(subdir)]
    )
    patched_dt_from_ts.assert_called_once_with(expected)


def test_storage_stat_no_subdirs(mocker, tmp_path):
    storage_path = tmp_path

    mocker.patch("pathlib.Path.glob", return_value=[])
    ts = 1754300000
    dt = datetime.fromtimestamp(ts)
    mocker.patch(
        "pathlib.Path.stat",
        return_value=stat_result(
            [16832, -1, -1, 2, 1000, 1000, 4096, ts, ts, ts]
        ),
    )
    mocker.patch(
        "qualibrate_config.core.project.p_list._created_at_from_storage",
        return_value=dt,
    )
    mocker.patch(
        "qualibrate_config.core.project.p_list._last_modified_at_from_storage",
        return_value=dt,
    )

    result = p_list._storage_stat(storage_path)
    assert result == (0, dt, dt)


def test_project_stat_dir(mocker, tmp_path):
    c_ts = 1754300000
    m_ts = 1754400000
    c_dt = datetime.fromtimestamp(c_ts)
    m_dt = datetime.fromtimestamp(m_ts)
    project_stat = stat_result(
        [16832, -1, -1, 2, 1000, 1000, 4096, 1754000000, m_ts, c_ts]
    )
    mocker.patch("pathlib.Path.stat", return_value=project_stat)
    patched_dt_from_ts = mocker.patch(
        "qualibrate_config.core.project.p_list._dt_from_ts",
        side_effect=[c_dt, m_dt],
    )
    result = p_list._project_stat_dir(tmp_path)
    assert result == (0, c_dt, m_dt)
    patched_dt_from_ts.assert_has_calls([mocker.call(c_ts), mocker.call(m_ts)])


def test_project_stat_with_existing_storage_dir(mocker, tmp_path):
    project = "proj"
    project_path = tmp_path / project
    project_path.mkdir()
    config_path = tmp_path / "config.toml"
    storage_path = tmp_path / "storage"
    storage_path.mkdir()

    mocker.patch(
        "qualibrate_config.core.project.p_list.get_project_path",
        return_value=project_path,
    )
    mocker.patch(
        "qualibrate_config.core.project.p_list.read_config_file",
        return_value={
            "qualibrate": {"storage": {"location": str(storage_path)}}
        },
    )
    mocker.patch(
        "qualibrate_config.core.project.p_list._storage_stat",
        return_value=(3, datetime.now(), datetime.now()),
    )

    project_obj = p_list.project_stat(tmp_path, project, config_path)
    assert project_obj.name == project
    assert isinstance(project_obj.created_at, datetime)


def test_project_stat_with_no_storage_defined(mocker, tmp_path):
    project = "proj"
    project_path = tmp_path / project
    project_path.mkdir()
    config_path = tmp_path / "config.toml"

    mocker.patch(
        "qualibrate_config.core.project.p_list.get_project_path",
        return_value=project_path,
    )
    mocker.patch(
        "qualibrate_config.core.project.p_list.read_config_file",
        return_value={},
    )
    mocker.patch(
        "qualibrate_config.core.project.p_list._project_stat_dir",
        return_value=(0, datetime.now(), datetime.now()),
    )

    project_obj = p_list.project_stat(tmp_path, project, config_path)
    assert project_obj.name == project
    assert isinstance(project_obj.last_modified_at, datetime)


def test_list_projects_with_two_dirs(mocker, tmp_path):
    projects = [tmp_path / "p1", tmp_path / "p2"]
    for p in projects:
        p.mkdir()

    mock_path = mocker.patch(
        "qualibrate_config.core.project.p_list.get_projects_path",
        return_value=tmp_path,
    )
    result = p_list.list_projects(tmp_path)
    assert set(result) == {"p1", "p2"}
    mock_path.assert_called_once_with(tmp_path)


def test_verbose_list_projects(mocker, tmp_path):
    mocker.patch(
        "qualibrate_config.core.project.p_list.list_projects",
        return_value=["p1", "p2"],
    )
    mocker.patch(
        "qualibrate_config.core.project.p_list.project_stat",
        return_value=p_list.Project(
            name="p1",
            nodes_number=1,
            created_at=datetime.now().astimezone(),
            last_modified_at=datetime.now().astimezone(),
        ),
    )

    result = p_list.verbose_list_projects(tmp_path / "config.toml")
    assert "p1" in result
    assert isinstance(result["p1"], p_list.Project)


def test_print_simple_projects_list(mocker, capsys, tmp_path):
    mocker.patch(
        "qualibrate_config.core.project.p_list.list_projects",
        return_value=["x", "y"],
    )
    p_list.print_simple_projects_list(tmp_path / "config.toml")
    out = capsys.readouterr().out
    assert "x" in out and "y" in out


def test_print_verbose_projects_list(mocker, capsys, tmp_path):
    now = datetime.now().astimezone()
    mock_proj = p_list.Project(
        name="proj", nodes_number=4, created_at=now, last_modified_at=now
    )
    mocker.patch(
        "qualibrate_config.core.project.p_list.verbose_list_projects",
        return_value={"proj": mock_proj},
    )
    p_list.print_verbose_projects_list(tmp_path / "config.toml")
    out = capsys.readouterr().out
    assert "Project 'proj'" in out
    assert "nodes_number" in out
