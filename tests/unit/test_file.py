import pytest
import tomli_w

from qualibrate_config import file as qc_file
from qualibrate_config.vars import DEFAULT_CONFIG_FILENAME


@pytest.fixture
def config_dir(tmp_path):
    """Fixture to create a temporary config directory with files."""
    config_file = tmp_path / "custom_config.toml"
    with config_file.open("wb") as f:
        tomli_w.dump({"key": "value"}, f)
    default_file = tmp_path / DEFAULT_CONFIG_FILENAME
    with default_file.open("wb") as f:
        tomli_w.dump({"default_key": "default_value"}, f)
    return tmp_path


def test_get_config_file_from_dir_with_specific_file(config_dir):
    specific_filename = "custom_config.toml"
    result = qc_file._get_config_file_from_dir(config_dir, specific_filename)
    assert result == config_dir / specific_filename


def test_get_config_file_from_dir_with_default_file(config_dir):
    result = qc_file._get_config_file_from_dir(config_dir, "nonexistent.toml")
    assert result == config_dir / DEFAULT_CONFIG_FILENAME


def test_get_config_file_from_dir_not_exists(config_dir):
    with pytest.raises(FileNotFoundError):
        qc_file._get_config_file_from_dir(config_dir / "empty", "config.toml")


def test_get_config_file_with_path(config_dir):
    specific_file = config_dir / "config.toml"
    result = qc_file.get_config_file(specific_file, "nonexistent.toml")
    assert result == specific_file, "Should return the specific file path."


def test_get_config_file_with_directory(config_dir):
    result = qc_file.get_config_file(config_dir, "config.toml")
    assert result == config_dir / "config.toml"


def test_get_config_file_not_exists_raise(config_dir):
    with pytest.raises(OSError):
        qc_file.get_config_file(config_dir / "nonexistent.toml", "config.toml")


def test_get_config_file_not_exists_skip(config_dir):
    file = config_dir / "nonexistent.toml"
    result = qc_file.get_config_file(file, "config.toml", False)
    assert result == file


def test_get_config_file_with_none_path(mocker, config_dir):
    mocker.patch("qualibrate_config.file.QUALIBRATE_PATH", config_dir)
    result = qc_file.get_config_file(None, "config.toml")
    assert result == config_dir / "config.toml"


def test_read_config_file_without_references(config_dir):
    config_file = config_dir / DEFAULT_CONFIG_FILENAME
    result = qc_file.read_config_file(config_file, solve_references=False)
    assert result == {"default_key": "default_value"}


def test_read_config_file_with_references(mocker, config_dir):
    config_file = config_dir / DEFAULT_CONFIG_FILENAME
    mocked_resolve_refs = mocker.patch(
        "qualibrate_config.file.resolve_references",
        return_value={"resolved_key": "resolved_value"},
    )
    result = qc_file.read_config_file(config_file)
    assert result == {"resolved_key": "resolved_value"}
    mocked_resolve_refs.assert_called_once_with(
        {"default_key": "default_value"}
    )
