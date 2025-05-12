import pytest

from qualibrate_config import validation
from qualibrate_config.models import QualibrateConfig


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
