from typing import get_origin

from pydantic_settings import BaseSettings

from qualibrate_config.models.base.referenced_type import ReferencedType

_BaseConfigAttributes = dir(BaseSettings)


class BaseReferencedSettings(BaseSettings):
    def __getattribute__(self, attr_name):
        attr = super().__getattribute__(attr_name)
        if attr_name in _BaseConfigAttributes:
            return attr
        field = self.model_fields.get(attr_name)
        if field is None:
            raise AttributeError(f"There is no field {attr_name}")
        origin = get_origin(field.annotation)
        if origin is None or not issubclass(origin, ReferencedType):
            return attr
        return attr.get_value()
