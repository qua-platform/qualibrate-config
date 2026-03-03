from qualibrate_config.models.base.config_base import BaseConfig

__all__ = ["DBConfig", "DatabaseStateConfig"]


class DBConfig(BaseConfig):
    host: str
    port: int
    database: str
    username: str | None = None
    password: str | None = None


class DatabaseStateConfig(BaseConfig):
    is_connected: bool = False
