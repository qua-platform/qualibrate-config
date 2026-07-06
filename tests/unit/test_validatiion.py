import pytest

from qualibrate_config import validation
from qualibrate_config.models import QualibrateConfig


@pytest.fixture(autouse=True)
def _reset_deprecated_subconfigs_warned_state():
    validation._WARNED_DEPRECATED_SUBCONFIGS.clear()


def test_qualibrate_version_validator_no_qualibrate_skip():
    assert validation.qualibrate_version_validator({}) is None


def test_qualibrate_version_validator_no_qualibrate_not_skip():
    with pytest.raises(validation.InvalidQualibrateConfigVersionError) as ex:
        validation.qualibrate_version_validator({}, skip_if_none=False)
    assert ex.value.args == ("Qualibrate config has no 'qualibrate' key",)
    assert ex.value.passed_version is None
    assert ex.value.supported_version == QualibrateConfig.version


def test_qualibrate_version_validator_no_version_skip():
    assert validation.qualibrate_version_validator({"qualibrate": {}}) is None


def test_qualibrate_version_validator_no_version_not_skip():
    with pytest.raises(validation.InvalidQualibrateConfigVersionError) as ex:
        validation.qualibrate_version_validator(
            {"qualibrate": {}}, skip_if_none=False
        )
    assert ex.value.args == (
        (
            "QUAlibrate was unable to load the config. Can't parse version "
            "of qualibrate config. Please run `qualibrate-config config`."
        ),
    )
    assert ex.value.passed_version is None
    assert ex.value.supported_version == QualibrateConfig.version


def test_qualibrate_version_validator_non_int_version():
    with pytest.raises(validation.InvalidQualibrateConfigVersionError) as ex:
        validation.qualibrate_version_validator(
            {"qualibrate": {"version": "v1"}}
        )
    assert ex.value.args == (
        (
            "QUAlibrate was unable to load the config. Can't parse version "
            "of qualibrate config. Please run `qualibrate-config config`."
        ),
    )
    assert ex.value.passed_version == "v1"
    assert ex.value.supported_version == QualibrateConfig.version


def test_qualibrate_version_validator_version_lower():
    with pytest.raises(validation.InvalidQualibrateConfigVersionError) as ex:
        validation.qualibrate_version_validator({"qualibrate": {"version": 1}})
    assert ex.value.args == (
        (
            "You have old version of config. Please run "
            "`qualibrate-config migrate`."
        ),
    )
    assert ex.value.passed_version == 1
    assert ex.value.supported_version == QualibrateConfig.version


def test_qualibrate_version_validator_version_greater():
    with pytest.raises(
        validation.GreaterThanSupportedQualibrateConfigVersionError
    ) as ex:
        validation.qualibrate_version_validator(
            {"qualibrate": {"version": QualibrateConfig.version + 1}}
        )
    assert ex.value.args == (
        (
            "You have config version greater than supported. "
            "Please update your qualibrate-config package "
            "(pip install --upgrade qualibrate-config)."
        ),
    )
    assert ex.value.passed_version == QualibrateConfig.version + 1
    assert ex.value.supported_version == QualibrateConfig.version


def test_qualibrate_version_validator_valid():
    assert (
        validation.qualibrate_version_validator(
            {"qualibrate": {"version": QualibrateConfig.version}}
        )
        is None
    )


def test_deprecated_subconfigs_validator_none_present(capsys):
    validation.deprecated_subconfigs_validator({"qualibrate": {"storage": {}}})
    assert capsys.readouterr().out == ""


def test_deprecated_subconfigs_validator_all_present(capsys):
    validation.deprecated_subconfigs_validator(
        {
            "qualibrate": {
                "app": {"static_site_files": "/tmp/static"},
                "runner": {
                    "address": "http://127.0.0.1:8001/execution/",
                    "timeout": 1.0,
                },
                "composite": {
                    "app": {"spawn": True},
                    "runner": {"spawn": True},
                },
            }
        }
    )
    out = capsys.readouterr().out
    for path in (
        "runner.address",
        "runner.timeout",
        "app.static_site_files",
        "composite.app",
        "composite.runner",
    ):
        assert path in out
    assert "1.5.0" in out


def test_deprecated_subconfigs_validator_warns_once_per_run(capsys):
    config = {
        "qualibrate": {
            "runner": {"address": "http://127.0.0.1:8001/execution/"},
        }
    }
    validation.deprecated_subconfigs_validator(config)
    assert "runner.address" in capsys.readouterr().out

    validation.deprecated_subconfigs_validator(config)
    assert capsys.readouterr().out == ""


def test_deprecated_subconfigs_validator_unrelated_app_settings_not_warned(
    capsys,
):
    # `app`/`runner` namespaces may gain new, unrelated settings in the
    # future — only the specific retired leaf paths should warn.
    validation.deprecated_subconfigs_validator(
        {
            "qualibrate": {
                "app": {"timeline_db": {"address": "x", "timeout": 1.0}},
                "runner": {},
                "composite": {"qua_dashboards": {"spawn": True}},
            }
        }
    )
    assert capsys.readouterr().out == ""
