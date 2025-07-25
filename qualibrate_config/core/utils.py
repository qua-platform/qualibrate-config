from collections.abc import Mapping
from typing import Any

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
