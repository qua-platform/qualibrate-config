from typing import Any

import click

__all__ = ["DeprecatedOption"]


class DeprecatedOption(click.Option):
    def __init__(
        self,
        *args: Any,
        preferred: str | None = None,
        deprecated: tuple[str] | None = None,
        message: str | None = None,
        **kwargs: Any,
    ):
        self.__deprecated = deprecated or ()
        self.__preferred = preferred or args[0][-1]
        self.__message = message
        super().__init__(*args, **kwargs)

    @property
    def deprecated_preferred(self) -> tuple[tuple[str, ...], str]:
        return self.__deprecated, self.__preferred

    @property
    def message(self) -> str | None:
        """Custom deprecation message.

        Used instead of the default "use `preferred` instead" text for
        options that are deprecated outright, with no replacement option.
        """
        return self.__message
