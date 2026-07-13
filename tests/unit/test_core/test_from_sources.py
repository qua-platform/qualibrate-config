import click

from qualibrate_config.core.from_sources import _get_runner_config


def _make_ctx(params: dict) -> click.Context:
    """Build a minimal Click context with no CLI-sourced params."""
    cmd = click.Command("test")
    ctx = click.Context(cmd)
    ctx.params = params
    return ctx


class TestGetRunnerConfig:
    def test_old_qualibrate_seeds_address_and_timeout_defaults(self, mocker):
        mocker.patch(
            "qualibrate_config.core.from_sources.qualibrate_supports_single_backend",
            return_value=False,
        )
        ctx = _make_ctx({"runner_address": None, "runner_timeout": None})
        result = _get_runner_config(ctx, {})

        assert result["address"] == "http://127.0.0.1:8001/execution/"
        assert result["timeout"] == 1.0

    def test_old_qualibrate_preserves_existing_file_values(self, mocker):
        mocker.patch(
            "qualibrate_config.core.from_sources.qualibrate_supports_single_backend",
            return_value=False,
        )
        ctx = _make_ctx({"runner_address": None, "runner_timeout": None})
        existing = {"address": "http://custom:9000/", "timeout": 5.0}
        result = _get_runner_config(ctx, existing)

        assert result["address"] == "http://custom:9000/"
        assert result["timeout"] == 5.0

    def test_new_qualibrate_does_not_seed_defaults(self, mocker):
        mocker.patch(
            "qualibrate_config.core.from_sources.qualibrate_supports_single_backend",
            return_value=True,
        )
        ctx = _make_ctx({"runner_address": None, "runner_timeout": None})
        result = _get_runner_config(ctx, {})

        assert "address" not in result
        assert "timeout" not in result
