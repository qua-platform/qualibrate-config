from pydantic import BaseModel

__all__ = ["Versioned"]


class Versioned(BaseModel):
    config_version: int = 1
