from typing import Any

import click

__all__ = ["DeprecatedOption"]


class DeprecatedOption(click.Option):
    def __init__(
        self,
        *args: Any,
        preferred: str | None = None,
        deprecated: tuple[str] | None = None,
        **kwargs: Any,
    ):
        self.__deprecated = deprecated or ()
        self.__preferred = preferred or args[0][-1]
        super().__init__(*args, **kwargs)

    @property
    def deprecated_preferred(self) -> tuple[tuple[str, ...], str]:
        return self.__deprecated, self.__preferred
