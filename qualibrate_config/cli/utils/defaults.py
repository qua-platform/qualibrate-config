from importlib.util import find_spec
from pathlib import Path

from qualibrate_config.vars import QUALIBRATE_CONFIG_KEY, QUALIBRATE_PATH


def get_qapp_static_file_path() -> Path:
    qualibrate_app = find_spec("qualibrate_app")
    if qualibrate_app is not None and qualibrate_app.origin is not None:
        return Path(qualibrate_app.origin).parents[1] / "qualibrate_static"
    static = QUALIBRATE_PATH / "qualibrate_static"
    static.mkdir(parents=True, exist_ok=True)
    return static


def get_user_storage() -> Path:
    return QUALIBRATE_PATH.joinpath(
        "user_storage", f"${{#/{QUALIBRATE_CONFIG_KEY}/project}}"
    )
