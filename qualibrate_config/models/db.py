from qualibrate_config.models.base.config_base import BaseConfig

__all__ = ["DBConfig", "DatabaseStateConfig"]


class DBConfig(BaseConfig):
    host: str
    port: int
    database: str
    username: str | None = None
    password: str | None = None
    table_name: str = "machine_state"


class DatabaseStateConfig(BaseConfig):
    is_connected: bool = False
