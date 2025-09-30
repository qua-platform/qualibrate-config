import functools
import warnings
from collections.abc import Callable
from typing import Any, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])
C = TypeVar("C", bound=type[Any])


def deprecated_alias(
    *, name: str, deprecated_module: str, new_module: str
) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(
                f"'{name}' from '{deprecated_module}.{name}' "
                f"is deprecated. Use '{new_module}.{name}' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapped  # type: ignore

    return decorator


def deprecated_class_alias(
    *, name: str, deprecated_module: str, new_module: str
) -> Callable[[C], C]:
    """Decorator for classes."""

    def decorator(cls: C) -> C:
        class Wrapped(cls):  # type: ignore[misc, valid-type]
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                warnings.warn(
                    f"'{name}' from '{deprecated_module}.{name}' "
                    f"is deprecated. Use '{new_module}.{name}' instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )
                super().__init__(*args, **kwargs)

        Wrapped.__name__ = cls.__name__
        Wrapped.__doc__ = cls.__doc__
        Wrapped.__module__ = cls.__module__
        return cast(C, Wrapped)

    return decorator
