from typing import Any

from pydantic import BaseModel, Field


class Reference(BaseModel):
    config_path: str
    reference_path: str
    index_start: int
    index_end: int
    value: Any = None
    solved: bool = False

    def __hash__(self) -> int:
        return hash(
            (
                self.config_path,
                self.reference_path,
                self.index_start,
                self.index_end,
            )
        )


class PathWithSolvingReferences(BaseModel):
    config_path: str
    value: Any = None
    solved: bool = False
    references: list[Reference] = Field(default_factory=list)
