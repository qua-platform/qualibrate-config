from inspect import isclass
from typing import Annotated, Any, Generic, Optional, Union, cast, get_origin

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from typing_extensions import TypeVar, get_args

from qualibrate_config.references.resolvers import (
    TEMPLATE_START,
    resolve_single_item,
)
from qualibrate_config.storage import STORAGE

__all__ = ["ReferencedType", "ModelReferencedType", "is_referenced_type"]

T = TypeVar("T")


class ReferencedType(Generic[T]):
    value: Optional[T]
    referenced_value: Optional[str]
    _type: Optional[type[T]]

    def __init__(
        self,
        value: Optional[T] = None,
        referenced_value: Optional[str] = None,
        _type: Optional[type[T]] = None,
    ):
        if not (
            (value is not None and referenced_value is None)
            or (referenced_value is not None and _type is not None)
        ):
            raise ValueError(
                f"Only one of value({value}) or "
                f"referenced_value({referenced_value}) can be specified."
            )
        self.value = value
        self.referenced_value = referenced_value
        self._type = _type

    def get_value(self) -> T:
        if self.value is not None:
            return self.value
        value = resolve_single_item(STORAGE, cast(str, self.referenced_value))
        return self._type(value)  # type: ignore

    def set_value(self, value: Union[str, T]) -> None:
        # TODO: should we allow overwrite references or values?
        is_passed_ref = isinstance(value, str) and TEMPLATE_START in value
        expected_type = cast(
            type, type(self.value) if self.value is not None else self._type
        )
        if is_passed_ref:
            # passed ref
            ref = str(value)
            resolved_value = resolve_single_item(STORAGE, ref)
            try:
                expected_type(resolved_value)
            except ValueError as ex:
                raise ValueError(
                    f"Invalid argument type. Passed reference: {value}. "
                    f"Resolved to value {resolved_value} "
                    f"(type = {type(resolved_value)}). "
                    f"Expected: {expected_type}"
                ) from ex
            self.referenced_value = ref
        else:
            try:
                self.value = expected_type(value)
            except ValueError as ex:
                raise ValueError(
                    f"Invalid argument type. Passed: {type(value)}. "
                    f"Expected: {expected_type}"
                ) from ex

    def __str__(self) -> str:
        return f"{self.value}({self.referenced_value})"

    def __repr__(self) -> str:
        return (
            f"ReferencedType(value={self.value}, "
            f"reference={self.referenced_value})"
        )


class _ReferencedTypePydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        arg = get_args(source_type)[0]
        template_type = (
            get_args(arg)[0] if get_origin(arg) is Annotated else arg
        )
        type_schema = handler.generate_schema(template_type)

        def validate_from_value(value: Any) -> ReferencedType[T]:
            if isinstance(value, str) and TEMPLATE_START in value:
                return ReferencedType(None, value, template_type)
            try:
                built = template_type(value)
                return ReferencedType(built, None)
            except TypeError:
                raise

        from_template_schema = core_schema.union_schema(
            [
                core_schema.no_info_plain_validator_function(
                    validate_from_value
                ),
                type_schema,
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_template_schema,
            python_schema=core_schema.union_schema(
                [
                    # if it's an instance first before doing any further work
                    core_schema.is_instance_schema(ReferencedType),
                    from_template_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.get_value(),
            ),
        )


ModelReferencedType = Annotated[
    ReferencedType[T], _ReferencedTypePydanticAnnotation
]


def is_referenced_type(arg: type) -> bool:
    if not isclass(arg):
        return False
    try:
        return issubclass(arg, ReferencedType)
    except TypeError:
        raise
