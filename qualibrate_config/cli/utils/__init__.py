import functools
import warnings
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


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
