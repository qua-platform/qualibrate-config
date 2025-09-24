from collections.abc import Callable, Sequence
from types import MethodType
from typing import Any

import click
from click.core import Option as CoreOption
from click.parser import Option as ParserOption
from click.parser import ParsingState

from qualibrate_config.cli.deprecated.deprecated_option import DeprecatedOption

__all__ = ["DeprecatedOptionsCommand"]


def _validate_deprecated_option(
    option: CoreOption,
) -> tuple[Sequence[str], str]:
    assert isinstance(option, DeprecatedOption)
    deprecated, preferred = option.deprecated_preferred
    msg = "Expected `deprecated` value for `{}`"
    assert deprecated is not None, msg.format(option.name)
    return deprecated, preferred


def make_deprecated_process(
    option: ParserOption,
) -> Callable[[ParserOption, Any, ParsingState], None]:
    """Construct a closure to the parser option processor"""
    option_instance = option.obj
    original_process = option.process
    deprecated, preferred = _validate_deprecated_option(option_instance)

    def process(self: ParserOption, value: Any, state: ParsingState) -> None:
        """The function above us on the stack used 'opt' to
        pick option from a dict, see if it is deprecated"""
        # reach up the stack and get 'opt'
        import inspect

        frame = inspect.currentframe()
        if frame is None:
            return original_process(value, state)
        opt = None
        try:
            if frame.f_back is not None:
                opt = frame.f_back.f_locals.get("opt")
        finally:
            del frame
        if opt in deprecated:
            msg = "'{}' has been deprecated, use '{}'"
            click.secho(msg.format(opt, preferred), fg="yellow")

        return original_process(value, state)

    return process


class DeprecatedOptionsCommand(click.Command):
    def make_parser(self, ctx: click.Context) -> click.OptionParser:
        """Hook 'make_parser' and during processing check the name
        used to invoke the option to see if it is preferred"""

        parser = super().make_parser(ctx)

        # get the parser options
        options = set(parser._short_opt.values())
        options |= set(parser._long_opt.values())
        for option in options:
            if isinstance(option.obj, DeprecatedOption):
                option.process = MethodType(  # type: ignore
                    make_deprecated_process(option), option
                )

        return parser
