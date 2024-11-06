from pathlib import Path

__all__ = ["QUALIBRATE_PATH", "DEFAULT_CONFIG_FILENAME"]


QUALIBRATE_PATH = Path().home() / ".qualibrate"
DEFAULT_CONFIG_FILENAME = "config.toml"
