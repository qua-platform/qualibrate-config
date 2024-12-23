import importlib
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    ClassVar,
    Optional,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from pydantic_core._pydantic_core import ValidationError

from qualibrate_config.models.base.importable import Importable
from qualibrate_config.models.base.path_serializer import PathSerializer
from qualibrate_config.qulibrate_types import RawConfigType
from qualibrate_config.references.resolvers import (
    TEMPLATE_START,
    resolve_single_item,
)

__all__ = ["BaseConfig"]


class BaseConfig:
    """
    A base class for handling nested configuration with type annotations,
    default values, optional fields, and attribute-style access.
    """

    _root: ClassVar[Optional["BaseConfig"]] = None

    def __init__(
        self,
        config: RawConfigType,
        path: Optional[str] = None,
        root: Optional["BaseConfig"] = None,
    ) -> None:
        """
        Initializes the configuration object with the provided dictionary.
        Supports nested configurations, default values, and optional fields.
        """
        self._path = path or "/"
        self._data: RawConfigType = {}
        self._annotations = self.get_annotations()
        self._raw_dict: RawConfigType = {}
        self.__class__._root = root or self

        for key, value_type in self._annotations.items():
            # Default value from class or set to None
            default_value = getattr(self.__class__, key, None)
            # Get value from config or use default
            value = config.get(key, default_value)

            value = self._parse_value(key, value, value_type)
            self._set_config_attr(key, value)

    def _set_config_attr(self, key: str, value: Any) -> None:
        raw_value = value._raw_dict if isinstance(value, BaseConfig) else value
        self._raw_dict[key] = raw_value
        self._data[key] = value

    def _is_reference_key(self, attr_name: str) -> bool:
        if attr_name not in self._annotations:
            return False
        attr_value = self._data[attr_name]
        return self._is_reference(attr_value)

    @staticmethod
    def _is_reference(attr_value: Any) -> bool:
        return isinstance(attr_value, str) and TEMPLATE_START in attr_value

    def _get_referenced_value(self, attr_name: str) -> Any:
        if attr_name not in self._annotations:
            raise AttributeError(
                f"{self.__class__.__name__} has no attribute {attr_name}"
            )
        reference = self._data.get(attr_name)
        if reference is None:
            raise ValueError(f"Attribute {attr_name} has no reference")
        return resolve_single_item(self._get_root()._data, reference)

    @classmethod
    def _get_root(cls) -> "BaseConfig":
        if cls._root is None:
            raise RuntimeError("Root can't be None")
        return cls._root

    def _parse_type_origin(
        self, key: str, value: Any, expected_type: type
    ) -> Any:
        error_path = ("/", *filter(bool, self._path.split("/")), key)
        if issubclass(expected_type, list):
            if not isinstance(value, list):
                from pydantic_core import InitErrorDetails

                raise ValidationError.from_exception_data(
                    f"value must be list, got {type(value).__name__}.",
                    line_errors=[
                        InitErrorDetails(
                            type="InvalidType",
                            loc=error_path,
                            input=value,
                        )
                    ],
                )
            # TODO: check args type
            return value

        if issubclass(expected_type, dict):
            # Handle dict types
            if not isinstance(value, dict):
                raise ValueError(
                    f"Field '{key}' expects a dict, got {type(value).__name__}."
                )
            # TODO: check args type
            return value

        if issubclass(expected_type, BaseConfig):
            # Handle nested configuration
            path = f"{self._path.rstrip('/')}/{key}"
            if isinstance(value, expected_type):
                value._path = path
                return value
            if isinstance(value, dict):
                return expected_type(value, path=path, root=self._get_root())
            raise ValueError(
                f"Field '{key}' expects a dictionary for nested config, "
                f"got {type(value).__name__}."
            )

        if issubclass(expected_type, Enum):
            return expected_type(value)
        if issubclass(expected_type, Path):
            return Path(value)

        if issubclass(expected_type, Importable) and isinstance(value, str):
            return value
        return None

    def _parse_value(self, key: str, value: Any, expected_type: type) -> Any:
        """
        Parses and validates a value based on the expected type.

        """
        origin = get_origin(expected_type) or expected_type
        args = get_args(expected_type)

        if origin is Union:
            # Handle Union types, including Optional (Union[..., None])
            if type(None) in args and value is None:
                return value
            exs: list[Exception] = []
            for arg in args:
                try:
                    return self._parse_value(key, value, arg)
                except (TypeError, ValueError) as ex:
                    exs.append(ex)
            raise ValueError(
                f"Field '{key}' expects one of {args}, "
                f"got {type(value).__name__}."
            ) from RuntimeError(exs)

        if isinstance(origin, type):
            result = self._parse_type_origin(key, value, origin)
            if result is not None:
                return result
        if self._is_reference(value):
            return value

        # Validate primitive types
        if issubclass(origin, float) and isinstance(value, int):
            return origin(value)
        if not isinstance(value, origin):
            raise ValueError(
                f"Field '{key}' expects {expected_type.__name__}, "
                f"got {type(value).__name__}."
            )
        return value

    @classmethod
    def get_annotations(cls) -> dict[str, type]:
        """
        Collect annotations from the current class and its ancestors.
        Handles inheritance correctly.
        """
        annotations = {}
        for parent in reversed(cls.__mro__):
            if issubclass(parent, BaseConfig):
                annotations.update(get_type_hints(parent))
        annotations.pop("_root", None)
        return annotations

    def serialize(self, exclude_none: bool = True) -> RawConfigType:
        def _get_val(val: Any) -> Any:
            if isinstance(val, BaseConfig):
                return val.serialize()
            if isinstance(val, Path):
                return PathSerializer.serialize_path(val)
            if isinstance(val, Enum):
                return val.value
            return val

        conditions: list[Callable[[str, Any], bool]] = []
        if exclude_none:
            conditions.append(lambda k, v: v is not None)
        return {
            key: _get_val(value)
            for key, value in self._data.items()
            if (
                len(conditions) == 0
                or all(condition(key, value) for condition in conditions)
            )
        }

    def __getattribute__(self, name: str) -> Any:
        """
        Custom getter for attributes.

        :param name: Attribute name to access.
        :return: Attribute value or raises AttributeError if not found.
        """
        if name in ConfigBaseDir:
            res = super().__getattribute__(name)
            return res
        annotations = self._annotations
        if name in annotations:
            data = self._data
            if name not in data:
                raise AttributeError(
                    f"There is no {name} in {self.__class__.__name__}."
                )
            value = data[name]
            if self._is_reference(value):
                if self.__class__._root is None:
                    raise ValueError("Root shouldn't be None")
                raw_dict = self._get_root()._raw_dict
                return resolve_single_item(raw_dict, value)
            annotation = annotations[name]
            annotation_type = get_origin(annotation) or annotation
            if not isinstance(annotation_type, type):
                return value
            if issubclass(annotation_type, Importable):
                module, class_ = value.rsplit(".", maxsplit=1)
                class_module = importlib.import_module(module)
                return getattr(class_module, class_)
            if issubclass(annotation_type, Path):
                path_str = PathSerializer.serialize_path(value)
                if not self._is_reference(path_str):
                    return value
                raw_dict = self._get_root()._raw_dict
                resolved_path = resolve_single_item(raw_dict, path_str)
                return Path(resolved_path)
            return value
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Custom setter for attributes.

        :param name: Attribute name to set.
        :param value: Value to assign to the attribute.
        """
        if name in ConfigBaseDir:
            super().__setattr__(name, value)
            return
        if name not in self._annotations:
            super().__setattr__(name, value)
            return
        expected_type = self._annotations[name]
        value = self._parse_value(name, value, expected_type)
        self._set_config_attr(name, value)


ConfigBaseDir = (
    *dir(BaseConfig),
    "_path",
    "_data",
    "_annotations",
    "_raw_dict",
)
