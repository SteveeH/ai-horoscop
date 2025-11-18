from typing import Any

from bson.objectid import ObjectId
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


def validate_ObjectId(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except BaseException as exc:
        raise ValueError(f"Invalid ObjectId format : {id_str}") from exc


class PydanticObjectId(ObjectId):
    """Pydantic v2 compatible ObjectId type for MongoDB."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """
        Pydantic v2 core schema for ObjectId validation.
        Supports both ObjectId instances and string representations.
        """
        return core_schema.union_schema(
            [
                # Accept ObjectId instances directly
                core_schema.is_instance_schema(ObjectId),
                # Accept strings and validate them
                core_schema.no_info_plain_validator_function(cls.validate),
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        """Validate and convert input to ObjectId."""
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            return validate_ObjectId(v)
        raise ValueError(f"Invalid ObjectId type : {type(v)}")

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, _handler: Any
    ) -> dict[str, Any]:
        """JSON schema representation for OpenAPI/JSON Schema."""
        return {"type": "string", "format": "ObjectId"}


# Export models for convenience
__all__ = ["PydanticObjectId"]
