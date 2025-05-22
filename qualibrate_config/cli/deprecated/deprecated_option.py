from typing import Any, Optional

import click

__all__ = ["DeprecatedOption"]


class DeprecatedOption(click.Option):
    def __init__(
        self,
        *args: Any,
        preferred: Optional[str] = None,
        deprecated: Optional[tuple[str]] = None,
        **kwargs: Any,
    ):
        self.__deprecated = deprecated or ()
        self.__preferred = preferred or args[0][-1]
        super().__init__(*args, **kwargs)

    @property
    def deprecated_preferred(self) -> tuple[tuple[str, ...], str]:
        return self.__deprecated, self.__preferred
