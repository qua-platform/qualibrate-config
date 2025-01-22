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
        self.deprecated = deprecated or ()
        self.preferred = preferred or args[0][-1]
        super().__init__(*args, **kwargs)
