from qualibrate_config.models.base.config_base import BaseConfig

__all__ = ["DBConfig"]


class DBConfig(BaseConfig):
    host: str
    port: int
    database: str
    username: str | None = None
    password: str | None = None