from collections.abc import Callable
from functools import cached_property
from typing import Any


class DefaultConfigValue:
    def __init__(
        self,
        value: Any = None,
        factory: Callable[[], Any] | None = None,
    ):
        if value and factory:
            raise ValueError("Cannot set both factory and value")
        if value is None and factory is None:
            raise ValueError("Cannot set `None` both factory and value")
        self._value = value
        self._factory = factory

    @cached_property
    def value(self) -> Any:
        if self._factory is not None and self._value is None:
            self._value = self._factory()
        return self._value
