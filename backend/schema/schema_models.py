from typing import Any
from pydantic import BaseModel, Field


class FieldSchema(BaseModel):
    path: str
    types: list[str] = Field(default_factory=list)
    sample_values: list[Any] = Field(default_factory=list)


class CollectionSchema(BaseModel):
    collection: str
    fields: list[FieldSchema] = Field(default_factory=list)