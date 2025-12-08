import pytest

from qualibrate_config.core.utils import recursive_update_dict


def test_recursive_update_dict_add_new_key():
    """Test that new keys from updates are added to the base dict."""
    base = {"section": {"existing": "value"}}
    updates = {"section": {"new_key": "new_value"}}

    result = recursive_update_dict(base, updates)

    assert result["section"]["existing"] == "value"
    assert result["section"]["new_key"] == "new_value"


def test_recursive_update_dict_update_existing_key():
    """Test that existing keys are properly updated."""
    base = {"section": {"key": "old_value"}}
    updates = {"section": {"key": "new_value"}}

    result = recursive_update_dict(base, updates)

    assert result["section"]["key"] == "new_value"


def test_recursive_update_dict_add_new_top_level_section():
    """Test that completely new sections are added."""
    base = {"existing_section": {"key": "value"}}
    updates = {"new_section": {"key": "value"}}

    result = recursive_update_dict(base, updates)

    assert "existing_section" in result
    assert "new_section" in result
    assert result["new_section"]["key"] == "value"


def test_recursive_update_dict_nested_merge_with_new_keys():
    """Test recursive merge preserves existing nested values while adding new ones."""
    base = {
        "quam": {
            "version": 3,
            "serialization": {"include_defaults": True}
        }
    }
    updates = {
        "quam": {
            "state_path": "/new/path",
            "serialization": {"other_option": False}
        }
    }

    result = recursive_update_dict(base, updates)

    # Existing values preserved
    assert result["quam"]["version"] == 3
    assert result["quam"]["serialization"]["include_defaults"] is True

    # New values added
    assert result["quam"]["state_path"] == "/new/path"
    assert result["quam"]["serialization"]["other_option"] is False


def test_recursive_update_dict_project_config_use_case():
    """
    Test the real-world use case: project config adding state_path
    when base config doesn't have it.

    This was the bug scenario:
    - Base config: [quam] has version=3, no state_path
    - Project config: [quam] adds state_path="/project/path"
    - Expected: state_path should be merged in
    - Bug (before fix): state_path was skipped
    """
    # Base config from ~/.qualibrate/config.toml
    base = {
        "quam": {
            "raise_error_missing_reference": False,
            "version": 3,
            "serialization": {"include_defaults": True}
        },
        "qualibrate": {
            "version": 5,
            "project": "CS_1"
        }
    }

    # Project config from ~/.qualibrate/projects/CS_1/config.toml
    updates = {
        "quam": {
            "state_path": "/path/to/project/quam_state"
        },
        "qualibrate": {
            "storage": {"location": "/project/storage"}
        }
    }

    result = recursive_update_dict(base, updates)

    # Verify all base values preserved
    assert result["quam"]["version"] == 3
    assert result["quam"]["raise_error_missing_reference"] is False
    assert result["quam"]["serialization"]["include_defaults"] is True
    assert result["qualibrate"]["version"] == 5
    assert result["qualibrate"]["project"] == "CS_1"

    # Verify new project-specific values added (this was the bug!)
    assert result["quam"]["state_path"] == "/path/to/project/quam_state"
    assert result["qualibrate"]["storage"]["location"] == "/project/storage"


def test_recursive_update_dict_empty_updates():
    """Test that empty updates dict doesn't break anything."""
    base = {"section": {"key": "value"}}
    updates = {}

    result = recursive_update_dict(base, updates)

    assert result == base


def test_recursive_update_dict_non_dict_value_override():
    """Test that non-dict values properly override nested dicts."""
    base = {"section": {"key": {"nested": "value"}}}
    updates = {"section": {"key": "simple_value"}}

    result = recursive_update_dict(base, updates)

    assert result["section"]["key"] == "simple_value"


def test_recursive_update_dict_multiple_new_keys_at_different_levels():
    """Test adding new keys at multiple nesting levels."""
    base = {
        "level1": {
            "level2": {
                "existing": "value"
            }
        }
    }
    updates = {
        "level1": {
            "new_at_level2": "value2",
            "level2": {
                "new_at_level3": "value3"
            }
        }
    }

    result = recursive_update_dict(base, updates)

    assert result["level1"]["level2"]["existing"] == "value"
    assert result["level1"]["new_at_level2"] == "value2"
    assert result["level1"]["level2"]["new_at_level3"] == "value3"
