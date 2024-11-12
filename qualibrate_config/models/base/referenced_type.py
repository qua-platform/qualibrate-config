from typing import Any, Generic, Optional

from pydantic_core import core_schema
from typing_extensions import Annotated, TypeVar, get_args

from pydantic import (
    GetCoreSchemaHandler,
    ValidationError,
)

from qualibrate_config.references.resolvers import TEMPLATE_START


__all__ = ["ReferencedType", "ModelReferencedType"]

T = TypeVar("T")


class ReferencedType(Generic[T]):
    value: T
    reference: str

    def __init__(
        self, value: Optional[T] = None, reference: Optional[str] = None
    ):
        self.value = value
        self.reference = reference

    def get_value(self):
        return self.value or f"will be resolved: {self.reference}"

    def __str__(self):
        return f"{self.value}({self.reference})"

    def __repr__(self):
        return f"ReferencedType(value={self.value}, reference={self.reference})"


class _ReferencedTypePydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        args = get_args(source_type)
        template_type = args[0]
        type_schema = handler.generate_schema(template_type)

        def validate_from_value(value: Any) -> ReferencedType:
            if isinstance(value, template_type):
                return ReferencedType(value, None)
            if isinstance(value, str) and TEMPLATE_START in value:
                return ReferencedType(None, value)
            raise ValidationError("Unexpected type")

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
                    # check if it's an instance first before doing any further work
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
