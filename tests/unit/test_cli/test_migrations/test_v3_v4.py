import sys
from copy import deepcopy

from qualibrate_config.core.migration.migrations import v3_v4

CONFIG_V3 = {
    "qualibrate": {
        "project": "init_project",
        "log_folder": "/home/user/.qualibrate/logs",
        "version": 3,
        "storage": {
            "type": "local_storage",
            "location": (
                "/home/user/.qualibrate/user_storage/${#/qualibrate/project}"
            ),
        },
        "app": {
            "static_site_files": (
                "/home/user/.venv/lib/python3.11/site-packages/qualibrate_static"
            )
        },
        "runner": {
            "address": "http://127.0.0.1:8001/execution/",
            "timeout": 1.0,
        },
        "composite": {
            "app": {"spawn": True},
            "runner": {"spawn": True},
            "qua_dashboards": {"spawn": True},
        },
        "calibration_library": {
            "folder": "/home/user/.qualibrate/calibrations",
            "resolver": "qualibrate.QualibrationLibrary",
        },
    }
}


def test_migrate_v3_v4_default_static(tmp_path):
    config_v3 = deepcopy(CONFIG_V3)
    config_v4_migrated = v3_v4.Migrate.forward(config_v3, tmp_path)
    config_v4_expected = config_v3
    config_v4_expected["qualibrate"]["app"].pop("static_site_files")
    config_v4_expected["qualibrate"]["version"] = 4
    assert config_v4_expected == config_v4_migrated


def test_migrate_v3_v4_custom_static(tmp_path):
    config_v3 = deepcopy(CONFIG_V3)
    config_v3["qualibrate"]["app"]["static_site_files"] = (
        "/home/user/custom_static"
    )
    config_v4_migrated = v3_v4.Migrate.forward(config_v3, tmp_path)
    config_v4_expected = config_v3
    config_v4_expected["qualibrate"]["version"] = 4
    assert config_v4_expected == config_v4_migrated


def test_migrate_v4_v3_with_static(tmp_path):
    config_v3_expected = CONFIG_V3
    config_v4 = deepcopy(CONFIG_V3)
    config_v4["qualibrate"]["version"] = 4
    config_v3_migrated = v3_v4.Migrate.backward(config_v4, tmp_path)
    assert config_v3_expected == config_v3_migrated


def test_migrate_v4_v3_without_static_no_app(tmp_path):
    config_v4 = deepcopy(CONFIG_V3)
    config_v4["qualibrate"]["version"] = 4
    config_v4["qualibrate"]["app"].pop("static_site_files")
    config_v3_migrated = v3_v4.Migrate.backward(config_v4, tmp_path)
    config_v3_expected = config_v4
    config_v3_expected["qualibrate"]["version"] = 3
    assert config_v3_expected == config_v3_migrated


def test_migrate_v4_v3_without_static_app_exists(mocker, tmp_path):
    config_v4 = deepcopy(CONFIG_V3)
    config_v4["qualibrate"]["version"] = 4
    config_v4["qualibrate"]["app"].pop("static_site_files")
    # Simulate `qualibrate_app` being installed at tmp_path by creating the
    # package dir and pointing sys.path at tmp_path. The migration's sys.path
    # walk will then find it and derive the static_site_files from its parent.
    (tmp_path / "qualibrate_app").mkdir()
    mocker.patch.object(sys, "path", [str(tmp_path)])
    config_v3_migrated = v3_v4.Migrate.backward(config_v4, tmp_path)
    config_v3_expected = deepcopy(CONFIG_V3)
    config_v3_expected["qualibrate"]["app"]["static_site_files"] = str(
        tmp_path / "qualibrate_static"
    )
    assert config_v3_expected == config_v3_migrated
