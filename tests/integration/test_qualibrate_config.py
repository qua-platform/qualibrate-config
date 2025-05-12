from pathlib import Path

import pytest

from qualibrate_config.models import (
    QuaDashboardSubServiceConfig,
    QualibrateAppConfig,
    QualibrateAppSubServiceConfig,
    QualibrateCompositeConfig,
    QualibrateConfig,
    QualibrateRunnerRemoteServiceConfig,
    QualibrateRunnerSubServiceConfig,
    StorageConfig,
    StorageType,
)


def test_minified_model():
    conf_dict = {
        "project": "init_project",
        "storage": {
            "type": "local_storage",
            "location": "/tmp/user_storage/${#/project}",
        },
    }
    conf = QualibrateConfig(conf_dict)

    assert isinstance(conf.storage, StorageConfig)
    assert conf.app is None
    assert conf.runner is None
    assert conf.composite is None
    assert conf.calibration_library is None

    assert conf.version == 4
    assert conf.project == "init_project"
    assert conf.log_folder is None
    assert conf.storage.type == StorageType.local_storage
    assert conf.storage.location == Path("/tmp/user_storage/init_project")


def test_full_model():
    conf_dict = {
        "version": 4,
        "project": "init_project",
        "log_folder": "/tmp/logs",
        "app": {"static_site_files": "/tmp/qualibrate_static"},
        "storage": {
            "type": "local_storage",
            "location": "/tmp/user_storage/${#/project}",
        },
        "runner": {
            "address": "http://localhost:8001/execution/",
            "timeout": 1.0,
        },
        "composite": {
            "app": {"spawn": True},
            "runner": {"spawn": True},
            "qua_dashboards": {"spawn": False},
        },
        "calibration_library": {
            "resolver": "qualibrate.qualibration_library.QualibrationLibrary",
            "folder": "/tmp/calibrations",
        },
    }
    conf = QualibrateConfig(conf_dict)

    assert isinstance(conf.app, QualibrateAppConfig)
    assert isinstance(conf.storage, StorageConfig)
    assert isinstance(conf.runner, QualibrateRunnerRemoteServiceConfig)
    assert isinstance(conf.composite, QualibrateCompositeConfig)
    assert isinstance(conf.composite.app, QualibrateAppSubServiceConfig)
    assert isinstance(conf.composite.runner, QualibrateRunnerSubServiceConfig)
    assert isinstance(
        conf.composite.qua_dashboards, QuaDashboardSubServiceConfig
    )

    assert conf.version == 4
    assert conf.project == "init_project"
    assert conf.log_folder == Path("/tmp/logs")
    assert conf.app.static_site_files == Path("/tmp/qualibrate_static")
    assert conf.storage.type == StorageType.local_storage
    assert conf.storage.location == Path("/tmp/user_storage/init_project")
    assert conf.runner.address == "http://localhost:8001/execution/"
    assert conf.runner.timeout == 1.0
    assert conf.composite.app.spawn is True
    assert conf.composite.runner.spawn is True
    assert conf.composite.qua_dashboards.spawn is False
    assert conf.calibration_library.folder == Path("/tmp/calibrations")
    with pytest.raises(ImportError):
        conf.calibration_library.resolver  # noqa: B018
