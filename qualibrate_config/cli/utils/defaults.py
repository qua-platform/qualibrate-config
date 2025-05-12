from pathlib import Path

from qualibrate_config.vars import QUALIBRATE_CONFIG_KEY, QUALIBRATE_PATH


def get_user_storage() -> Path:
    return QUALIBRATE_PATH.joinpath(
        "user_storage", f"${{#/{QUALIBRATE_CONFIG_KEY}/project}}"
    )
