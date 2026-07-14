from copy import deepcopy

from qualibrate_config.core.migration.migrations import v5_v6

CONFIG_V5 = {
    "qualibrate": {
        "project": "init_project",
        "log_folder": "/home/user/.qualibrate/logs",
        "version": 5,
        "storage": {
            "type": "local_storage",
            "location": (
                "/home/user/.qualibrate/user_storage/${#/qualibrate/project}"
            ),
        },
        "app": {"static_site_files": "/home/user/custom_static"},
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


def test_migrate_v5_v6_copies_static_site_files(tmp_path):
    config_v5 = deepcopy(CONFIG_V5)
    config_v6_migrated = v5_v6.Migrate.forward(config_v5, tmp_path)
    config_v6_expected = deepcopy(CONFIG_V5)
    config_v6_expected["qualibrate"]["version"] = 6
    config_v6_expected["qualibrate"]["composite"]["static_site_files"] = (
        "/home/user/custom_static"
    )
    assert config_v6_expected == config_v6_migrated


def test_migrate_v5_v6_no_app_static_site_files(tmp_path):
    config_v5 = deepcopy(CONFIG_V5)
    config_v5["qualibrate"].pop("app")
    config_v6_migrated = v5_v6.Migrate.forward(config_v5, tmp_path)
    config_v6_expected = deepcopy(config_v5)
    config_v6_expected["qualibrate"]["version"] = 6
    assert config_v6_expected == config_v6_migrated


def test_migrate_v5_v6_composite_static_site_files_already_set(tmp_path):
    config_v5 = deepcopy(CONFIG_V5)
    config_v5["qualibrate"]["composite"]["static_site_files"] = (
        "/home/user/other_static"
    )
    config_v6_migrated = v5_v6.Migrate.forward(config_v5, tmp_path)
    config_v6_expected = deepcopy(config_v5)
    config_v6_expected["qualibrate"]["version"] = 6
    assert config_v6_expected == config_v6_migrated


def test_migrate_v6_v5_removes_composite_static_site_files(tmp_path):
    config_v6 = deepcopy(CONFIG_V5)
    config_v6["qualibrate"]["version"] = 6
    config_v6["qualibrate"]["composite"]["static_site_files"] = (
        "/home/user/custom_static"
    )
    config_v5_migrated = v5_v6.Migrate.backward(config_v6, tmp_path)
    config_v5_expected = CONFIG_V5
    assert config_v5_expected == config_v5_migrated


def test_migrate_v6_v5_no_composite(tmp_path):
    config_v6 = deepcopy(CONFIG_V5)
    config_v6["qualibrate"].pop("composite")
    config_v6["qualibrate"]["version"] = 6
    config_v5_migrated = v5_v6.Migrate.backward(config_v6, tmp_path)
    config_v5_expected = deepcopy(config_v6)
    config_v5_expected["qualibrate"]["version"] = 5
    assert config_v5_expected == config_v5_migrated
