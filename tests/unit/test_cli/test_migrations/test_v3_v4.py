from copy import deepcopy
from importlib.util import find_spec
from pathlib import Path

from qualibrate_config.cli.migrations import v3_v4

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
            "address": "http://localhost:8001/execution/",
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


def test_migrate_v3_v4_default_static():
    config_v3 = deepcopy(CONFIG_V3)
    config_v4_migrated = v3_v4.Migrate.forward(config_v3)
    config_v4_expected = config_v3
    config_v4_expected["qualibrate"]["app"].pop("static_site_files")
    config_v4_expected["qualibrate"]["version"] = 4
    assert config_v4_expected == config_v4_migrated


def test_migrate_v3_v4_custom_static():
    config_v3 = deepcopy(CONFIG_V3)
    config_v3["qualibrate"]["app"]["static_site_files"] = (
        "/home/user/custom_static"
    )
    config_v4_migrated = v3_v4.Migrate.forward(config_v3)
    config_v4_expected = config_v3
    config_v4_expected["qualibrate"]["version"] = 4
    assert config_v4_expected == config_v4_migrated


def test_migrate_v4_v3_with_static():
    config_v3_expected = CONFIG_V3
    config_v4 = deepcopy(CONFIG_V3)
    config_v4["qualibrate"]["version"] = 4
    config_v3_migrated = v3_v4.Migrate.backward(config_v4)
    assert config_v3_expected == config_v3_migrated


def test_migrate_v4_v3_without_static_no_app(mocker):
    config_v4 = deepcopy(CONFIG_V3)
    config_v4["qualibrate"]["version"] = 4
    config_v4["qualibrate"]["app"].pop("static_site_files")
    config_v3_migrated = v3_v4.Migrate.backward(config_v4)
    config_v3_expected = config_v4
    config_v3_expected["qualibrate"]["version"] = 3
    assert config_v3_expected == config_v3_migrated


def test_migrate_v4_v3_without_static_app_exists(mocker):
    config_v4 = deepcopy(CONFIG_V3)
    config_v4["qualibrate"]["version"] = 4
    config_v4["qualibrate"]["app"].pop("static_site_files")
    config_spec = find_spec("qualibrate_config")
    mocker.patch(
        "qualibrate_config.cli.migrations.v3_v4.find_spec",
        return_value=config_spec,
    )
    config_v3_migrated = v3_v4.Migrate.backward(config_v4)
    config_v3_expected = deepcopy(CONFIG_V3)
    config_v3_expected["qualibrate"]["app"]["static_site_files"] = str(
        Path(config_spec.origin).parents[1] / "qualibrate_static"
    )
    assert config_v3_expected == config_v3_migrated
