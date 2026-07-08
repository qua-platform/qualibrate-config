from pathlib import Path

from qualibrate_config.models.q_app import get_default_static_path


def test_returns_none_when_no_sys_path_entry_has_static_dir(
    monkeypatch, tmp_path
):
    monkeypatch.setattr("sys.path", [str(tmp_path)])

    assert get_default_static_path() is None


def test_returns_first_matching_static_dir_on_sys_path(monkeypatch, tmp_path):
    empty_entry = tmp_path / "empty"
    empty_entry.mkdir()
    match_entry = tmp_path / "match"
    static_dir = match_entry / "qualibrate" / "app" / "qualibrate_static"
    static_dir.mkdir(parents=True)

    monkeypatch.setattr("sys.path", [str(empty_entry), str(match_entry)])

    assert get_default_static_path() == Path(static_dir)
