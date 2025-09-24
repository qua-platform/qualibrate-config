from collections.abc import Callable, Iterable, Mapping
from typing import Any, Protocol, TypeVar, overload

from qualibrate_config.qulibrate_types import RawConfigType


def recursive_update_dict(
    to_update: RawConfigType,
    updates: Mapping[str, Any],
) -> RawConfigType:
    for k, v in updates.items():
        if k not in to_update:
            continue
        if isinstance(v, Mapping):
            to_update[k] = recursive_update_dict(to_update.get(k, {}), v)
        else:
            to_update[k] = v
    return to_update


class SupportsRichComparison(Protocol):
    def __lt__(self, other: Any) -> bool: ...

    def __gt__(self, other: Any) -> bool: ...


T = TypeVar("T")
KT = TypeVar("KT", bound=SupportsRichComparison)
CT = TypeVar("CT", bound=SupportsRichComparison)
R1 = TypeVar("R1")
R2 = TypeVar("R2")


@overload
def minmax(
    iterable: Iterable[CT],
    *,
    key: None = ...,
    default: tuple[R1, R2] | None = ...,
) -> tuple[CT | R1, CT | R2]: ...


@overload
def minmax(
    iterable: Iterable[T],
    *,
    key: Callable[[T], KT],
    default: tuple[R1, R2] | None = ...,
) -> tuple[T | R1, T | R2]: ...


def minmax(
    iterable: Iterable[Any],
    *,
    key: Callable[[Any], Any] | None = None,
    default: tuple[Any, Any] | None = None,
) -> tuple[Any, Any]:
    it = iter(iterable)
    try:
        first = next(it)
    except StopIteration:
        if default is not None:
            return default
        raise ValueError("minmax() arg is an empty sequence") from None

    if key is None:
        min_key = max_key = first
        for elem in it:
            min_key, max_key, _, _ = _minmax(
                min_key, max_key, elem, min_key, max_key, elem
            )
        return min_key, max_key
    else:
        min_elem = max_elem = first
        min_key = max_key = key(first)
        for elem in it:
            min_key, max_key, min_elem, max_elem = _minmax(
                min_key, max_key, key(elem), min_elem, max_elem, elem
            )
        return min_elem, max_elem


def _minmax(
    min_key: KT,
    max_key: KT,
    k: KT,
    min_elem: T,
    max_elem: T,
    elem: T,
) -> tuple[KT, KT, T, T]:
    if k < min_key:
        min_elem, min_key = elem, k
    elif k > max_key:
        max_elem, max_key = elem, k
    return min_key, max_key, min_elem, max_elem
