import pytest

from qualibrate_config.models.remote_services import (
    QualibrateRunnerRemoteServiceConfig,
)


def test_address_with_root_raises_if_address_is_none():
    conf = QualibrateRunnerRemoteServiceConfig({"timeout": 1.0})

    with pytest.raises(ValueError, match="address is not set"):
        conf.address_with_root  # noqa: B018
