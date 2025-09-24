from collections.abc import Mapping
from io import StringIO
from typing import Annotated, Any

from pydantic import AwareDatetime, BaseModel, Field, field_serializer

from qualibrate_config.core.approve import print_config


class Project(BaseModel):
    name: str
    nodes_number: int
    created_at: AwareDatetime
    last_modified_at: AwareDatetime
    updates: Annotated[Mapping[str, Any], Field(default_factory=dict)]

    @field_serializer("created_at", "last_modified_at")
    def dt_serializer(self, dt: AwareDatetime) -> str:
        return dt.isoformat(timespec="seconds")

    def verbose_str(self) -> str:
        d = self.model_dump()
        d.pop("name")
        updates = d.pop("updates")
        if updates:
            updates_io = StringIO()
            print_config(updates, 2, updates_io)
            updates_str = "config overrides:\n" + updates_io.getvalue()
        else:
            updates_str = "config overrides: None"
        return f"\n{' ' * 4}".join(
            [
                f"Project: {self.name}",
                *[f"{k}: {v}" for k, v in d.items()],
                updates_str,
            ]
        ).rstrip("\n")
