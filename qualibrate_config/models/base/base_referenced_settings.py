from typing import Annotated, Any, Optional, Union, cast, get_args, get_origin

from pydantic import PrivateAttr
from pydantic_settings import BaseSettings

from qualibrate_config.models.base.referenced_type import (
    is_referenced_type,
)

_BaseConfigAttributes = dir(BaseSettings)


def _is_reference_field(annotation: Optional[type]) -> bool:
    origin = get_origin(annotation)
    if origin is None:
        return False
    args = tuple(
        (get_origin(get_args(arg)[0]) if get_origin(arg) is Annotated else arg)
        for arg in get_args(annotation)
    )
    return (
        origin is Union
        and any(is_referenced_type(arg) for arg in args if arg is not None)
    ) or is_referenced_type(origin)


class BaseReferencedSettings(BaseSettings):
    _is_referenced_fields: dict[str, bool] = PrivateAttr(default_factory=dict)

    def _is_ref(self, attr_name: str, annotation: Optional[type]) -> bool:
        # decrease amount of BaseReferencedSettings.__getattribute__ calls
        is_ref_dict = self._is_referenced_fields
        is_ref = is_ref_dict.get(attr_name)
        if is_ref is not None:
            return is_ref
        is_ref = _is_reference_field(annotation)
        is_ref_dict[attr_name] = is_ref
        return is_ref

    def __getattribute__(self, attr_name: str) -> Any:
        attr = super().__getattribute__(attr_name)
        if attr_name in _BaseConfigAttributes:
            return attr
        field = self.model_fields.get(attr_name)
        if field is None:
            raise AttributeError(f"There is no field {attr_name}")
        is_ref = self._is_ref(attr_name, field.annotation)
        if is_ref:
            return attr.get_value()
        return attr

    def get_reference(self, attr_name: str) -> Optional[str]:
        field = self.model_fields.get(attr_name)
        if field is None:
            raise AttributeError(f"There is no field {attr_name}")
        is_ref = self._is_ref(attr_name, field.annotation)
        if not is_ref:
            return None
        attr = super().__getattribute__(attr_name)
        return cast(Optional[str], attr.referenced_value)
